import asyncio
import random
import sys
import threading
from enum import Enum

import raft_pb2_grpc as pb2_grpc
import raft_pb2 as pb2
import logging
import traceback
import grpc
from concurrent import futures

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

CONFIG_PATH = "config.conf"

# HEARTBEAT_INTERVAL = 0.05
# ELECTION_TIMEOUT_MIN = 0.15
# ELECTION_TIMEOUT_MAX = 0.3


HEARTBEAT_INTERVAL = 0.1
ELECTION_TIMEOUT_MIN = 0.4
ELECTION_TIMEOUT_MAX = 0.6


class RaftState(Enum):
    Follower = 0
    Candidate = 1
    Leader = 2

def read_conf(path):
    with open(path, 'r') as f:
        lines = list(map(lambda l: l.split(), f.readlines()))
        return  list(map(lambda l: pb2.RaftAddress(id=int(l[0]), address=f"{l[1]}:{l[2]}"), lines))
    

class RaftRequestHandler(pb2_grpc.RaftServerServicer):
    def __init__(self, node):
        self.node = node
    
    def AppendEntries(self, request, context):
        # logging.debug(f"{self.prefix} Entered appending context")
        # with self.node.term_mutex:
        if self.node.leader_id is None:
            self.node.leader_id = request.nodeId
            
        if request.term == self.node.term:
            if self.node.leader_id == request.nodeId:
                return pb2.RaftResponse(term=request.term, success=True)
            return pb2.RaftResponse(term=request.term, success=False)
        elif request.term > self.node.term:
            self.node.become_follower(request.term, request.nodeId)
            return pb2.RaftResponse(term=request.term, success=True)
        else:
            return pb2.RaftResponse(term=self.node.term, success=False)
        # logging.debug(f"{self.prefix} Exited appending context")


    def RequestVote(self, request, context):
        if self.node.leader_id is None and self.node.term <= request.term:
            self.node.become_follower(request.term, request.nodeId)
            logging.info(f"{self.node.prefix} Voted for node {request.nodeId}")
            return pb2.RaftResponse(term=request.term, success=True)
        elif self.node.term < request.term or request.nodeId == self.node.id:
            self.node.become_follower(request.term, request.nodeId)
            logging.info(f"{self.node.prefix} Voted for node {request.nodeId}")
            return pb2.RaftResponse(term=request.term, success=True)
        else:
            return pb2.RaftResponse(term=self.node.term, success=False)


    def GetLeader(self, request, context):
        res = self.node.get_node_addr(self.node.leader_id)
        if res is None:
            res = pb2.RaftAddress(id=-1, address="")
        return res
    
    


#         rpc AppendEntries(RaftRequest) returns (RaftResponse);
# rpc GetLeader(TextMessage) returns (RaftAddress);

#*/ rpc Suspend(TextMessage) returns (TextMessage);
# rpc RequestVote(RaftRequest) returns (RaftResponse);
        

class RaftNode:
    def __init__(self, id):
        try:
            self.nodes = read_conf(CONFIG_PATH)
        except Exception as e:
            logging.debug(str(e))
            # logging.debug(traceback.format_exception())
        
        self.term, self.term_mutex = 0, threading.Lock()

        self.leader_id = None
        self.raft_entry = [x for x in self.nodes if x.id == id][0]
        self.addr, self.id = self.raft_entry.address, self.raft_entry.id
+-
+
        self.prefix = f"Node {self.id}:"
        
        self.connections, self.connection_mutex = {}, threading.Lock()
        
        self.init_connections()
        
        self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        # self.election_timeout = random.randint(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.election_timer = threading.Timer(self.election_timeout, self.become_candidate)
        self.heartbeat_timer = threading.Timer(HEARTBEAT_INTERVAL, self.broadcast_heartbeat)
        
        self.election_timer_mutex = threading.Lock()
        self.heartbeat_timer_mutex = threading.Lock()
        
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        
        pb2_grpc.add_RaftServerServicer_to_server(RaftRequestHandler(self), self.server)
        
        self.server.add_insecure_port(self.addr)
        
        logging.info(f"{self.prefix} The server starts at {self.addr}")
        self.server.start()
        
        self.become_follower(self.term, self.leader_id)
        
        try:
            self.server.wait_for_termination()
        except KeyboardInterrupt:
            logging.info(f"{self.prefix} Terminating the node")       
        
    def become_candidate(self):
        logging.info(f"The leader is dead")
        self.election_timer.cancel()
        self.heartbeat_timer.cancel()
        self.state = RaftState.Candidate
        # with self.term_mutex:
        self.term += 1
        logging.info(f"I am a candidate. Term {self.term}")
        
        n_votes, requests_failed = 0, 0
        
        for node in self.nodes:
            stub = self.connections[node.id]["stub"]
            req = pb2.RaftRequest(term=self.term, nodeId=self.id)
            try:
                res = stub.RequestVote(req)
                if res.term > self.term:
                    self.become_follower(res.term, res.nodeId)
                    return
                if res.success == True:
                    n_votes += 1
            except Exception as e:
                requests_failed += 1
                # logging.debug(traceback.format_exception())
                logging.debug(f"{self.prefix} unable to connect to node {node.id}")
                continue
        
        logging.info(f"Votes received. Total: {n_votes}")
        
        if n_votes > len(self.nodes) // 2:
            logging.debug("About to become leader")
            self.become_leader()
        elif n_votes < int(round(len(self.nodes) / 2)):
            self.become_follower(res.term)
        else:
            logging.debug("Received n // 2 number of votes. Going to reinitialize the voting")
            # logging.debug(f"{self.prefix} Entered election mutex context")
    
            # with self.election_timer_mutex:
            self.election_timeout = random.uniform(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
            self.election_timer = threading.Timer(self.election_timeout, self.become_candidate)
            self.election_timer.start()
            # logging.debug(f"{self.prefix}: Exited election mutex context")
            
    def become_leader(self):
        logging.info(f"{self.prefix} I am the leader. Term {self.term}")
        self.election_timer.cancel()
        self.state = RaftState.Leader
        self.broadcast_heartbeat()

    # async def _req_vote(self, stub, req):
    #     await stub.req
    #     print("<", tag)
    #     return tag
    
    def broadcast_heartbeat(self):
        req = pb2.RaftRequest(term=self.term, nodeId=self.id)

        # cond_var = threading.Condition(lock=None)
        # 
        # def process_response(call_future):
        #     print(call_future.result())
        logging.debug(f"Node {self.id} is Broadcasting heartbeat in term {self.term}")

        responses = [conn["stub"].AppendEntries.future(req) for conn in self.connections.values()]
        
        for response in responses:
            if not response.code() == grpc.StatusCode.OK:
                continue
            
            result = response.result()
            
            if result.term > self.term:
                self.become_follower(result.term)

        self.heartbeat_timer = threading.Timer(HEARTBEAT_INTERVAL, self.broadcast_heartbeat)
        self.heartbeat_timer.start()
            # if res.code == grpc.StatusCode.CANCELLED:
            #     pass
            # if res.code == grpc.StatusCode.UNAVAILABLE:
            #     pass
        # done, _ = futures.wait(fs, timeout=HEARTBEAT_INTERVAL, return_when=futures.ALL_COMPLETED)
        
        # for f in done:
        #     if f.exception() is not None:
        #         logging.debug("Failed broadcast to some node")
        #         continue
        #     if f.cancelled():
        #         continue
        #     
        #     res = f.result()
        #     if not res.success:
                
        
        # call_future.add_done_callback(process_response)
        
        # for conn in self.connections:
        #     try:
        #         res = conn["stub"].AppendEntries(req)
        #         if not res.success:
        #             self.become_follower(res.term, res.nodeId)
        #     except Exception:
        #         # logging.debug(traceback.format_exception())
        #         # logging.debug(f"{self.prefix}: unable to connect to the node ")
        #         continue
            
       
    
    def become_follower(self, term, leader_id=None):
        if term < self.term:
            logging.debug("Tried to become follower with lower term than current")
            return
        self.leader_id = leader_id
        self.heartbeat_timer.cancel()
        self.election_timer.cancel()
        self.state = RaftState.Follower
        self.term = term
        logging.info(f"{self.prefix} I am the follower. Term {term}")
        
        # logging.debug(f"Entered follower context")
        # with self.election_timer_mutex:
        self.election_timer = threading.Timer(self.election_timeout, self.become_candidate)
        self.election_timer.start()
        # logging.debug(f"Exited follower context")
                
    def init_connections(self):
        # with self.connection_mutex:
        for node in self.nodes:
            channel = grpc.insecure_channel(self.get_node_addr(node.id))
            stub = pb2_grpc.RaftServerStub(channel)
            self.connections[node.id] = {"channel":channel, "stub":stub}

# 
    # def get_connection(self, node_id):
    #     if self.connections[node_id] in self.connections:
    #         return self.connections[node_id]
    #     
    #     channel = grpc.insecure_channel(self.get_node_addr(node_id))
    #     stub = pb2_grpc.RaftServerStub(channel)
    #     
    #     
    #         
    # 
    # def clean_connection(self, node_id):
    #     with self.connection_mutex:
    #         del self.connections[node_id]
    # 
    def get_node_addr(self, node_id):
        for node in self.nodes:
            if node.id == node_id:
                return node.address
        return None

if len(sys.argv) > 1 and sys.argv[1].isdigit():
    id = int(sys.argv[1])
else:
    id = 1

node = RaftNode(id)