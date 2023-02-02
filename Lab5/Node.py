import os
import signal
import sys
import threading
import time
import zlib
import grpc
import chord_pb2_grpc as pb2_grpc
import chord_pb2 as pb2
import socket
from contextlib import closing
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

# !!! FOR DEBUGGING PURPOSES ONLY! DON'T FORGET TO SET
# IT TO FALSE DURING TESTING
fake_hash = False

debug = False

def handle_error(message=None, is_fatal=True):
    print(message)
    if (is_fatal):
        print("Terminating the node")
        os._exit(0)
        

class ClientConnectionHandler(pb2_grpc.ClientServerServiceStub):
    def __init__(self, node):
        super(pb2_grpc.ClientServerServiceStub, self).__init__()
        self.node = node

    def connect(self, request, context):
        print(f"{self.node.prefix} Client is connected to the node")
        return pb2.Response(is_success=True, message=f"node {self.node.id}")

    def get_info(self, request, context):
        logging.debug(f'Node id: {self.node.id}, predecessor id: {self.node.predecessor.id}, successor id: {self.node.successor.id}')
        print(f"{self.node.prefix} Providing information about the node to the client")
        res = pb2.Response(is_success=True, message=f"Node id: {self.node.id}")
        return pb2.GetInfoResponse(response=res, nodes=self.node.fingertable)

class CRUDHandler(pb2_grpc.CRUDService):
    def __init__(self, node):
        super(pb2_grpc.CRUDService, self).__init__()
        self.node = node

    # Handle client's save request
    # (in this case entry.key corresponds to the key entered by the client)
    def save(self, entry, context):
        hash = self.node.get_key(entry.key)

        self.node.predecessor_mutex.acquire()
        self.node.successor_mutex.acquire()
        responsible_node_id = self.node.key_lookup(hash)
        self.node.predecessor_mutex.release()
        self.node.successor_mutex.release()

        print(f"{self.node.prefix} Got request to save \"{entry.text}\" with key \"{hash}\"")

        if responsible_node_id == self.node.id:
            # Store text with a given key on current node
            print(f"{self.node.prefix} Trying to save {entry.text} with key {hash}")
            return pb2.Response(**self.node.save(hash, entry.text))
        else:
            # Store text with a given key on other node
            stub = self.node.active_nodes[responsible_node_id]["control_stub"]
            print(f"{self.node.prefix} Delegating saving data with key {hash} to node {responsible_node_id}")
            internal_entry = pb2.DataEntry(key=hash, text=entry.text)
            return stub.save(internal_entry)

    def find(self, request, context):
        hash = self.node.get_key(request.text)

        self.node.predecessor_mutex.acquire()
        self.node.successor_mutex.acquire()
        responsible_node_id = self.node.key_lookup(hash)
        self.node.predecessor_mutex.release()
        self.node.successor_mutex.release()

        print(f"{self.node.prefix} Got request to find \"{request.text}\"")

        if responsible_node_id == self.node.id:
            # Lookup for text with a given key on current node
            print(f"{self.node.prefix} Trying to find \"{request.text}\"")
            return pb2.Response(**self.node.find(request.text))
        else:
            # Lookup for text with a given key on other node
            print(f"{self.node.prefix} Delegating finding {request.text} to node {responsible_node_id}")
            stub = self.node.active_nodes[responsible_node_id]["crud_stub"]
            return stub.find(request)

    def remove(self, request, context):
        hash = self.node.get_key(request.text)

        self.node.predecessor_mutex.acquire()
        self.node.successor_mutex.acquire()
        responsible_node_id = self.node.key_lookup(hash)
        self.node.predecessor_mutex.release()
        self.node.successor_mutex.release()

        if responsible_node_id == self.node.id:
            # Try to remove key from the current node
            print(f"{self.node.prefix} Trying to remove \"{request.text}\"")
            return pb2.Response(**self.node.remove(hash, request.text))
        else:
            # Try to remove key from other node
            print(f"{self.node.prefix} Delegating removal of {request.text} to node {responsible_node_id}")
            stub = self.node.active_nodes[responsible_node_id]["crud_stub"]
            return stub.remove(request)


class NodeRequestHandler(pb2_grpc.NodeNodeService):
    def __init__(self, node):
        super(pb2_grpc.NodeNodeService, self).__init__()
        self.node = node

    # Delegate storage of some keys to newly joined node
    # (which is predecessor of current one)
    def pass_data(self, predecessor, context):

        # Point predecessor reference to newly joined node
        self.node.predecessor_mutex.acquire()
        self.node.predecessor = predecessor
        self.node.add_channel(predecessor)
        self.node.predecessor_mutex.release()
        
        entries = []
        self.node.data_mutex.acquire()

        # Gather data entries which should be passed to newly joined
        # node and remove them from the dictionary
        for key in list(self.node.data_dict):
            if key in range(self.node.predecessor.id, self.node.id + 1):
                entries.append(pb2.DataEntry(key=key, text=self.node.data_dict[key]))
                del self.node.data_dict[key]
            # elif self.node.id - self.node.predecessor.id < 0 and key > self.node.id:
            #     entries.append(pb2.DataEntry(key=key, text=self.node.data_dict[key]))
            #     del self.node.data_dict[key]
                
        self.node.data_mutex.release()

        res = pb2.Response(is_success=True, message="")
        return pb2.PassDataResponse(response=res, data=entries)

    # Obtain data from the predecessor who is about to leave the chord.
    # Update predecessor channel and reference. 
    def inherit(self, request, context):
        data = request.data

        self.node.data_mutex.acquire()
        for entry in data:
            self.node.data_dict[entry.key] = entry.text
        self.node.data_mutex.release()
        
        if request.predecessor.id != self.node.id:
            self.node.predecessor_mutex.acquire()
            self.node.add_channel(request.predecessor)
            self.node.predecessor = request.predecessor
            self.node.predecessor_mutex.release()
        else:
            self.node.predecessor = None
        return pb2.Response(is_success=True, message="")
    
    # Update reference to the successor and first entry in the
    # fingertable. Called by newly joined node and necessary
    # because successor might be needed before fingertable is
    # updated with polling.
    def update_successor(self, successor, context):
        self.sucessor_mutex.acquire()
        self.node.successor = successor
        self.node.add_channel(successor)
        self.node.sucessor_mutex.release()

        return pb2.Response(is_success=True, message="")
    
    # Handle save request from another node
    # (in this case entry.key corresponds to the internal id used to store data)
    def save(self, entry, context):
        hash = entry.key

        self.node.predecessor_mutex.acquire()
        self.node.successor_mutex.acquire()
        responsible_node_id = self.node.key_lookup(hash)
        self.node.predecessor_mutex.release()
        self.node.successor_mutex.release()
    
        print(f"{self.node.prefix} Got request to save \"{entry.text}\" with key \"{hash}\"")
    
        if responsible_node_id == self.node.id:
            # Store text with a given key on current node
            print(f"{self.node.prefix} Trying to save {entry.text} with key {hash}")
            return pb2.Response(**self.node.save(hash, entry.text))
        else:
            # Store text with a given key on other node
            stub = self.node.active_nodes[responsible_node_id]["control_stub"]
            print(f"{self.node.prefix} Delegating saving data with key {hash} to node {responsible_node_id}")
            return stub.save(entry)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

class Node:
    def __init__(self, node_addr):
        
        self.address = {
            "ip": node_addr.split(":")[0],
            "port": int(node_addr.split(":")[1])
        }

        # Trying to join the chord
        res = self.join_chord()

        # Exit if failed to join chord
        if res.id == -1:
            handle_error(res.message, is_fatal=True)
            
        self.id = res.id
        self.m = int(res.message)
        self.max_nodes = int(pow(2, self.m))
        self.prefix = f"Node {self.id}:"
        self.ft_mutex, self.data_mutex, self.nodes_mutex = Lock(), Lock(), Lock()
        self.predecessor_mutex, self.successor_mutex = Lock(), Lock()
        self.predecessor, self.successor = None, None
        self.data_dict = {}
        # RDP connections with nodes from fingertable and predecessor.
        self.active_nodes = {}
    
        print(f"{self.prefix} Joined the chord")
        
        # Retrieve fingertable from the registry
        # (also set successor and predecessor references)
        self.get_fingertable()
        
        # Initialize RDP sessions with nodes from retrieved fingertable
        self.update_channels()

        # Obtain corresponding data from the successor
        if self.successor is not None:
            self.obtain_data()
        
        # Add request handlers to node server
        self.server = grpc.server(ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_ClientServerServiceServicer_to_server(ClientConnectionHandler(self), self.server)
        pb2_grpc.add_CRUDServiceServicer_to_server(CRUDHandler(self), self.server)
        pb2_grpc.add_NodeNodeServiceServicer_to_server(NodeRequestHandler(self), self.server)
        
        # Start node server
        self.server.add_insecure_port(node_addr)
        self.server.start()
        print(f"{self.prefix} Started server")
        
        # Start fingertable polling
        self.ft_poller = StoppableThread(target=self.poll_fingertable, args=())
        self.ft_poller.start()
        
        # # Add signal handling
        # signal.signal(signal.SIGINT, self.quit)
        # signal.signal(signal.SIGTERM, self.quit)

        try:
            self.server.wait_for_termination()
        except KeyboardInterrupt:
            self.quit()

    def get_key(self, text: str):
        if fake_hash and text.isdigit():
            return int(text)
        
        hash_value = zlib.adler32(text.encode())
        return hash_value % 2 ** self.m
    def join_chord(self):
            global registry_addr
            channel = grpc.insecure_channel(registry_addr)
            self.registry_stub = pb2_grpc.NodeRegistryServiceStub(channel)
            req = pb2.Address(**self.address)
            res = self.registry_stub.register(req)
            self.id = res.id
            return res
    
    def deregister(self):
        print("Deregistering from the chord")
        self.registry_stub.deregister(pb2.IdMessage(id=self.id))
    def quit(self, signum=None, frame=None, message=None):
        if message is not None:
            print(message)

        self.ft_poller.stop()
        
        self.successor_mutex.acquire()
        self.data_mutex.acquire()

        self.deregister()
        
        if self.successor is None:
            print("Terminating the node.")
            self.successor_mutex.release()
            self.data_mutex.release()
            os._exit(0)
            
        print("Passing data to the successor.")
        successor_con = self.active_nodes[self.successor.id]
        data = [pb2.DataEntry(key=k, text=v) for k, v in self.data_dict.items()]
        req = pb2.InheritRequest(predecessor=self.predecessor, data=data)

        successor_con["control_stub"].inherit(req)
        
        self.data_mutex.release()
        self.successor_mutex.release()
        print("Terminating the node.")
        # sys.exit(0)
        os._exit(0)
    
    def get_fingertable(self):
        id_msg = pb2.IdMessage(id=self.id)
        try:
            res = self.registry_stub.populate_finger_table(id_msg)
        except Exception as e:
            handle_error("Unable to retrieve fingertable", is_fatal=True)
            
        if res.response.is_success is False:
            self.quit(message=res.message)

        with self.ft_mutex as ftm, self.predecessor_mutex as pm, self.successor_mutex as sm:
            if len(res.ft) > 0 and res.predecessor.id != -1 and res.predecessor.id != self.id:
                self.predecessor = res.predecessor
            else:
                self.predecessor = None
            if len(res.ft) > 0 and res.ft[0].id != self.id:
                self.successor = res.ft[0]
            else:
                self.successor = None
            self.fingertable = sorted(res.ft, key=lambda x: x.id)

    def poll_fingertable(self):
        print(f"{self.prefix} Started fingertable polling")
        while True:
            if self.ft_poller.is_stopped():
                return
            self.get_fingertable()
            self.update_channels()
            time.sleep(1)

    def find_free_port(self):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind((self.address["ip"], 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    # Finds responsible node for storing item with a given key.
    # Assuming that fingertable is sorted.
    def key_lookup(self, key: int):
        
        # Current node is responsible for the key
        if self.successor is None or self.predecessor is None:
            return self.id
        if key in range(self.predecessor.id + 1, self.id + 1):
            return self.id
        elif key in range(self.id + 1, self.successor.id + 1):
            return self.successor.id
        else:
            if key > self.fingertable[-1].id:
                return self.fingertable[-1].id            
            for i in range(len(self.fingertable)):
                if i == len(self.fingertable) - 1:
                    return self.fingertable[i].id
                if self.fingertable[i].id >= key and self.fingertable[i + 1].id >= key:
                    return self.fingertable[i].id
            
            return self.fingertable[-1]

        
    def save(self, key: int, text: str):
        is_success = True
        
        self.data_mutex.acquire()
        if key not in self.data_dict:
            self.data_dict[key] = text
            msg = f"{text} is saved in node {self.id}"
        else:
            is_success = False
            msg = f"Key {key} already exists on node {self.id}"
        self.data_mutex.release()
        
        if debug:
            self.quit()
        
        return {"is_success": is_success, "message": msg}
    
    def remove(self, key, text):
        
        self.data_mutex.acquire()
        
        if key in self.data_dict:
            message = f"{self.data_dict[key]} is removed from node {self.id}"
            del self.data_dict[key]
            is_success = True
        else:
            message = f"{text} does not exist in node {self.id}"
            is_success = False
        
        self.data_mutex.release()
        
        return {"is_success": is_success, "message": message}
        
    def update_channels(self):
        self.ft_mutex.acquire()
        self.nodes_mutex.acquire()

        new_connections = {}

        # Initialize RDP connections with new nodes
        for node in self.fingertable:
            if node.id not in self.active_nodes:
                control_channel = grpc.insecure_channel(f"{node.address.ip}:{node.address.port}")
                control_stub = pb2_grpc.NodeNodeServiceStub(control_channel)

                crud_channel = grpc.insecure_channel(f"{node.address.ip}:{node.address.port}")
                crud_stub = pb2_grpc.CRUDServiceStub(crud_channel)
                
                new_connections[node.id] = {"control_channel": control_channel, "control_stub": control_stub,
                                            "crud_channel": crud_channel, "crud_stub": crud_stub}
                
            else:
                new_connections[node.id] = self.active_nodes[node.id]
                del self.active_nodes[node.id]

        # Close RDP outdated channels
        for old_node in self.active_nodes.values():
            old_node["crud_channel"].close()
            old_node["control_channel"].close()

        # Update reference to active nodes dictionary
        self.active_nodes = new_connections

        self.ft_mutex.release()
        self.nodes_mutex.release()
    
    def add_channel(self, node):
        self.nodes_mutex.acquire()
        if node.id not in self.active_nodes:
            control_channel = grpc.insecure_channel(f"{node.address.ip}:{node.address.port}")
            control_stub = pb2_grpc.NodeNodeServiceStub(control_channel)

            crud_channel = grpc.insecure_channel(f"{node.address.ip}:{node.address.port}")
            crud_stub = pb2_grpc.CRUDServiceStub(crud_channel)

            self.active_nodes[node.id] = {"crud_channel": crud_channel, "crud_stub": crud_stub,
                                          "control_channel": control_channel, "control_stub": control_stub}
        self.nodes_mutex.release()
            
    def find(self, text):
        if self.data_mutex.locked():
            print("wtf")
        
        self.data_mutex.acquire()
        
        key = self.get_key(text)
        
        if key in self.data_dict:
            is_success = True
            msg = f"{text} is saved in node {self.id}"
        else:
            is_success = False
            msg = f"{text} is not saved in node {self.id}"

        self.data_mutex.release()

        return {"is_success": is_success, "message": msg}

    def obtain_data(self):
        self.ft_mutex.acquire()
        
        self.add_channel(self.predecessor)
        
        self.nodes_mutex.acquire()
        self.data_mutex.acquire()
        self.successor_mutex.acquire()
        self.predecessor_mutex.acquire()
        
        successor_conn = self.active_nodes[self.successor.id]
        
        addr = pb2.Address(**self.address)
        req = pb2.FingerTableItem(id=self.id, address=addr)
        res = successor_conn["control_stub"].pass_data(req)
        
        if not res.response.is_success:
            print("Was not able to retrieve data from the successor.")
            self.quit(message=res.response.message)

        for x in res.data:
            self.data_dict[x.key] = x.text

        # Keys might be stored on the predecessor if the node that just 
        # has joined the chord has the largest id
        predecessor_conn = self.active_nodes[self.predecessor.id]

        res = predecessor_conn["control_stub"].pass_data(req)
    
        if not res.response.is_success:
            print("Was not able to retrieve data from the predecessor.")
            self.quit(message=res.response.message)
    
        for x in res.data:
            self.data_dict[x.key] = x.text
        
        self.data_mutex.release()

        self.successor_mutex.release()
        self.predecessor_mutex.release()
        self.ft_mutex.release()
        self.nodes_mutex.release()


if len(sys.argv) > 2:
    node_addr = sys.argv[2]
    registry_addr = sys.argv[1]
else:
    node_addr = "localhost:3434"
    registry_addr = "localhost:5555"

node = Node(node_addr)



