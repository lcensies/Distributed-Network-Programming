import asyncio
import os
import random
import sys
import threading
from enum import Enum
from time import sleep

import raft_pb2_grpc as pb2_grpc
import raft_pb2 as pb2
import logging
import grpc
from concurrent import futures

log_level = logging.INFO
logging.basicConfig(stream=sys.stdout, level=log_level, format="%(message)s")

CONFIG_PATH = "config.conf"

HEARTBEAT_INTERVAL = 0.05
ELECTION_TIMEOUT_MIN = 0.15
ELECTION_TIMEOUT_MAX = 0.3

# HEARTBEAT_INTERVAL = 0.1
# ELECTION_TIMEOUT_MIN = 1
# ELECTION_TIMEOUT_MAX = 1.5

class RaftState(Enum):
    Follower = 0
    Candidate = 1
    Leader = 2
    Sleeping = 3

def read_conf(path):
    with open(path, 'r') as f:
        lines = list(map(lambda l: l.split(), f.readlines()))
        return  list(map(lambda l: pb2.RaftAddress(id=int(l[0]), address=f"{l[1]}:{l[2]}"), lines))

def port_in_use(port) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0

def get_node_addr(nodes, node_id):
    for node in nodes:
        if int(node.id) == int(node_id):
            return node.address
    return None

class RaftRequestHandler(pb2_grpc.RaftServerServicer):
    def __init__(self, node):
        self.node = node
    
    def AppendEntries(self, request, context):
        if self.node.leader_id is None:
            self.node.leader_id = request.nodeId
            self.node.reset_election_timer()
            return pb2.RaftResponse(term=request.term, success=True)
        if request.term == self.node.term:
            if self.node.leader_id == request.nodeId:
                self.node.reset_election_timer()
                return pb2.RaftResponse(term=request.term, success=True)
            return pb2.RaftResponse(term=request.term, success=False)
        elif request.term > self.node.term:
            self.node.become_follower(request.term, request.nodeId)
            return pb2.RaftResponse(term=request.term, success=True)
        else:
            return pb2.RaftResponse(term=self.node.term, success=False)
        # logging.debug(f"{self.prefix} Exited appending context")

    def RequestVote(self, request, context):
        logging.debug(f"{self.node.prefix}({self.node.state}) - {request.nodeId} tried to RequestVote")
        if request.nodeId == self.node.id:
            logging.info(f"{self.node.prefix}Voted for node {request.nodeId}")
            return pb2.RaftResponse(term=request.term, success=True)
        elif self.node.leader_id is None and self.node.term <= request.term:
            self.node.become_follower(request.term, request.nodeId)
            logging.info(f"{self.node.prefix}Voted for node {request.nodeId}")
            return pb2.RaftResponse(term=request.term, success=True)
        elif self.node.term < request.term:
            self.node.become_follower(request.term, request.nodeId)
            logging.info(f"{self.node.prefix}Voted for node {request.nodeId}")
            return pb2.RaftResponse(term=request.term, success=True)
        else:
            return pb2.RaftResponse(term=self.node.term, success=False)
    def GetLeader(self, request, context):        
        res = [x for x in self.node.nodes if x.id == self.node.leader_id][0]
        if res is None:
            res = pb2.RaftAddress(id=-1, address="")
        return res
    def Suspend(self, request, context):
        self.node.sleep_timeout = float(request.text)
        logging.info(f"Sleeping for {self.node.sleep_timeout} seconds")

        try:
            return pb2.TextMessage(text="")
        finally:
            self.node.suspend()
    
class RaftNode:
    def __init__(self, nodes, id):
        self.nodes = nodes
        self.addr, self.id = get_node_addr(nodes, id), id
        
        self.term, self.term_mutex = 0, threading.Lock()
        self.state, self.state_mutex = None, threading.Lock()
        self.leader_id, self.leader_id_mutex = None, threading.Lock()
        self.raft_entry = [x for x in self.nodes if x.id == id][0]
        self.sleep_timeout = None
        if log_level == logging.DEBUG:
            self.prefix = f"Node {self.id}:"
        else:
            self.prefix = ""
        self.connections = {}
        
        self.init_connections()
        
        self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        # self.election_timeout = random.randint(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.election_timer = threading.Timer(self.election_timeout, self.become_candidate, [self.term])
        self.heartbeat_timer = threading.Timer(HEARTBEAT_INTERVAL, self.broadcast_heartbeat)
        
        self.election_timer_mutex = threading.Lock()
        self.heartbeat_timer_mutex = threading.Lock()
        
        self.server = None
        self.start_server()

        try:
            while True:
                self.server.wait_for_termination()
                if self.sleep_timeout is not None:
                    sleep(self.sleep_timeout)
                    self.sleep_timeout = None
                    self.start_server()
        except KeyboardInterrupt:
            logging.info(f"{self.prefix}Terminating the node")
            os._exit(0)
    
    def reset_election_timer(self):
        self.election_timer.cancel()
        self.election_timer = threading.Timer(self.election_timeout, self.become_candidate, [self.term])
        self.election_timer.start()
    def suspend(self):
        self.election_timer.cancel()
        self.heartbeat_timer.cancel()
        self.server.stop(grace=None)
    def start_server(self):
        logging.info(f"{self.prefix}The server starts at {self.addr}")
        
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_RaftServerServicer_to_server(RaftRequestHandler(self), self.server)    
        self.server.add_insecure_port(self.addr)
        self.server.start()
        self.become_follower(self.term, self.leader_id)
    def become_candidate(self, term):
        self.term_mutex.acquire()
        
        if self.term > term:
            self.term_mutex.release()
            return
        
        logging.info(f"The leader is dead")
        self.election_timer.cancel()
        self.heartbeat_timer.cancel()
        self.state = RaftState.Candidate
        
        self.term += 1
        logging.info(f"I am a candidate. Term {self.term}")
        n_votes, requests_failed = 0, 0
        
        for node in self.nodes:
            stub = self.connections[node.id]["stub"]
            req = pb2.RaftRequest(term=self.term, nodeId=self.id)
            try:
                res = stub.RequestVote(req)
                if res.term > self.term:
                    if self.term_mutex.locked():
                        self.term_mutex.release()
                    self.term = res.term
                    self.become_follower(res.term, res.nodeId)
                    logging.debug(f"{self.prefix}received term number {res.term} from node {node.id} during election")
                    return
                if res.success == True:
                    n_votes += 1
                    logging.debug(f"{self.prefix}node {node.id} voted for me!")

            except Exception as e:
                        requests_failed += 1
                        logging.debug(f"{self.prefix}unable to connect to node {node.id}")
                        continue
        
        logging.info(f"Votes received. Total: {n_votes}")
        
        median = int(round(len(self.nodes) / 2))
        
        if n_votes > median:
            logging.debug(f"{self.prefix}About to become leader")
            if self.term_mutex.locked():
                self.term_mutex.release()
            self.become_leader(self.term)
            return
        elif n_votes < median:
            logging.debug(f"{self.prefix}Not enough votes. Becoming follower")
            if self.term_mutex.locked():
                self.term_mutex.release()
            self.become_follower(self.term)
            return
        else:
            logging.debug(f"{self.prefix}Reinitializing election")

            self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
            self.election_timer = threading.Timer(self.election_timeout, self.become_candidate, [self.term])
            if self.term_mutex.locked():
                self.term_mutex.release()
            self.election_timer.start()
    def become_leader(self, term):
        with self.term_mutex:
            if self.term > term:
                return
            logging.info(f"{self.prefix}I am the leader. Term {self.term}")
            self.election_timer.cancel()
            self.state = RaftState.Leader
        self.broadcast_heartbeat()

    def broadcast_heartbeat(self):
        self.term_mutex.acquire()
        # with self.term_mutex:
        req = pb2.RaftRequest(term=self.term, nodeId=self.id)

        logging.debug(f"Node {self.id} is Broadcasting heartbeat in term {self.term}")

        responses = [conn["stub"].AppendEntries.future(req) for conn in self.connections.values()]
        
        for response in responses:
            if not response.code() == grpc.StatusCode.OK:
                logging.debug(f"{self.prefix} {response.details()}")
                continue
            
            result = response.result()
            
            if result.term > self.term:
                logging.debug(f"{self.prefix}Received larger term {result.term}. Becoming follower.")
                self.term_mutex.release()
                self.become_follower(result.term)

        self.heartbeat_timer = threading.Timer(HEARTBEAT_INTERVAL, self.broadcast_heartbeat)
        if self.term_mutex.locked():
            self.term_mutex.release()
        
        self.heartbeat_timer.start()
    
    def become_follower(self, term, leader_id=None):
        with self.term_mutex:
            self.reset_election_timer()
            if term < self.term:
                logging.debug("Tried to become follower with lower term than current")
                return
            self.leader_id = leader_id
            self.heartbeat_timer.cancel()
            self.state = RaftState.Follower
            self.term = term
            logging.info(f"{self.prefix}I am the follower. Term {term}")
           
    def init_connections(self):
        # with self.connection_mutex:
        for node in self.nodes:
            channel = grpc.insecure_channel(get_node_addr(self.nodes, node.id))
            stub = pb2_grpc.RaftServerStub(channel)
            self.connections[node.id] = {"channel":channel, "stub":stub}

addresses = read_conf(CONFIG_PATH)

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    id = int(sys.argv[1])
    port = get_node_addr(addresses, id).split(":")[1]
    # No check for address since for lab we assume that nodes will run only at localhost
    if port_in_use(port):
        print("Port is busy")
        os._exit(0)
        
else:
    id = None
    for addr in addresses:
        port = addr.address.split(":")[1]
        if not port_in_use(port):
            id = addr.id
            break
    
    if id is None:
        print("No free slots left. Terminating.")
        os._exit(0)

node = RaftNode(addresses, id)