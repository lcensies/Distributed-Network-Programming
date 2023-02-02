import random
import signal
import sys
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc
import grpc
from concurrent.futures import ThreadPoolExecutor

if len(sys.argv) > 2:
    address, port = sys.argv[1].split(':')
    m = sys.argv[2]
else:
    address = "127.0.0.1"
    port = "5555"
    m = "5"

nodes = []
dummy_node = pb2.FingerTableItem(id=-1, address=pb2.Address(ip="", port=-1))
dummy_node_max = pb2.FingerTableItem(id=9999999, address=pb2.Address(ip="", port=-1))
debug = True

class RegistryHandler(pb2_grpc.NodeRegistryServiceServicer):

    def __init__(self):
        self.m = int(m)

    def find_pred(self, key):

        nodes_sorted = sorted(nodes, key=lambda x: x.id, reverse=True)

        key_node = nodes_sorted[0]
    
        for node in nodes_sorted:
            if node.id < key:
                key_node = node
                break
    
        return key_node

    def find(self, key):
        
        nodes_sorted = sorted(nodes, key=lambda x: x.id)
        
        key_node = nodes_sorted[0]
        
        for node in nodes_sorted:
            if node.id >= key:
                key_node = node
                break
        
        return key_node

    def register(self, request, context):
        random.seed(0)

        new_node_id = 0
        new_node_address = request

        if len(nodes) == 2 ** self.m - 1:
            node_register_response = {'id': -1, 'message': "Chord is full"}
            return pb2.NodeRegisterResponse(**node_register_response)

        while True:
            is_unique_id = True
            new_node_id = random.randint(0, 2 ** self.m - 1)

            for node in nodes:
                if node.id == new_node_id:
                    is_unique_id = False
                    continue

            if is_unique_id:
                break

        
        finger_table_item = pb2.FingerTableItem(id=new_node_id, address=new_node_address)

        nodes.append(finger_table_item)
        node_register_response = {'id': new_node_id, 'message': str(self.m)}

        return pb2.NodeRegisterResponse(**node_register_response)

    def deregister(self, request, context):
        for node in nodes:
            if node.id == request.id:
                nodes.remove(node)
                response = {'is_success': True, 'message': f'Node {id} has been deregistered'}
                return pb2.Response(**response)

        response = {'is_success': False, 'message': 'There is no such registered id'}
        return pb2.Response(**response)

    def populate_finger_table(self, node, context):
        finger_table = []
            
        if node.id < 0 or node.id > 2 ** int(self.m) - 1:
            response = {'is_success': False, 'message': "Given ID out of the boundaries"}
            return pb2.PopulateFingerTableResponse(response=response)

        for i in range(int(self.m)):
            finger_table.append(self.find((node.id + 2 ** i) % (2 ** int(self.m))))
        
        filtered = []
        
        for i in range(len(finger_table)):
            is_unique_id = True
            for j in range(len(filtered)):
                if filtered[j].id == finger_table[i].id:
                    is_unique_id = False
                    break
            if is_unique_id and finger_table[i].id != node.id:
                filtered.append(finger_table[i])

        predecessor = self.find_pred(node.id)
        
        if predecessor.id == node.id:
            predecessor = dummy_node
        
        response = {'is_success': True, 'message': ""}
        return pb2.PopulateFingerTableResponse(response=response, predecessor=predecessor, ft=filtered)


class ClientHandler(pb2_grpc.ClientServerServiceServicer):
    def get_info(self, request, context):
        return pb2.GetInfoResponse(nodes=nodes)

    def connect(self, request, context):
        print("Client is connected to the registry")
        return pb2.Response(is_success=True, message=f"registry")
        


server = grpc.server(ThreadPoolExecutor(max_workers=10))

pb2_grpc.add_NodeRegistryServiceServicer_to_server(RegistryHandler(), server)
pb2_grpc.add_ClientServerServiceServicer_to_server(ClientHandler(), server)

server.add_insecure_port(f"{address}:{port}")
server.start()

# # Add signal handling
# signal.signal(signal.SIGINT, quit)
# signal.signal(signal.SIGTERM, quit)

print(f"Registry is started")

try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print("Terminating the registry")