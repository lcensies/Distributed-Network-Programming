import random
import re
import sys
import grpc
import chord_pb2 as pb2
import chord_pb2_grpc as pb2_grpc

debug = False
debug_node = "127.0.0.1:3434"

msg = pb2.TextMessage(text="")

# connect_regex = re.compile("^connect \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:([1-9][0-9]{0,3}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$")
connect_regex = re.compile("^connect .*$")
get_info_regex = re.compile("^get_info$")
# save_regex = re.compile("^save .*$")
save_regex = re.compile("(?<=save ).*(\".*\" )(.*)")
find_regex = re.compile("^find .*$")
remove_regex = re.compile("^remove .*$")
registry_regex = re.compile("[Rr]egistry")
quit_regex = re.compile("^quit")


server_channel, server_stub, server_type = None, None, None
node_channel, node_stub = None, None

print("Client is started")

class NodeRepr:
    def __init__(self, node):
        self.node = node
    def __str__(self):
        return f"{self.node.id}\t{self.node.address.ip}:{self.node.address.port}"

def handle_error(message: str, e: Exception = None):
    global server_channel, server_stub, server_type, node_channel, node_stub
    
    print(message)
    
    if server_channel is not None:
        print("Closing RPC channel")
        server_channel.close()
    if node_channel is not None:
        node_channel.close()

    server_channel, server_stub, server_type = None, None, None
    node_channel, node_stub = None, None

def connect(remote_addr):
    global server_channel, msg, server_type, server_stub, node_stub, node_channel

    if server_channel is not None:
        server_channel.close()
    if node_channel is not None:
        node_channel.close()
    
    server_channel = grpc.insecure_channel(remote_addr)
    server_stub = pb2_grpc.ClientServerServiceStub(server_channel)
    response = None
    try:
        response = server_stub.connect(msg)
    except Exception:
        handle_error("Unable to connect to the server")
        return
    if not response.is_success:
        handle_error(response.message)
        return
    else:
        if re.search(registry_regex, response.message):
            server_type = "registry"
            node_stub, node_channel = None, None
        else:
            server_type = "node"
            node_channel = grpc.insecure_channel(remote_addr)
            node_stub = pb2_grpc.CRUDServiceStub(node_channel)
            
        print(f"Connected to the {response.message}")
def get_info():
    global server_channel, server_type, server_stub, msg
    if server_channel is None:
        print("Not connected to any kind of server")
        return
    try:
        response = server_stub.get_info(msg)
    except Exception:
        handle_error("Unable to retrieve information.")
    else:
        print('\n'.join(list(map(lambda x: str(NodeRepr(x)), response.nodes))))

def save(key, text):
    global server_channel, server_type, server_stub

    key = key.replace("\"", "")
    
    if server_channel is None:
        print("Not connected to any kind of server")
        return
    if re.search(registry_regex, server_type):
        print("Registry does not store the data")
        return
    try:
        response = node_stub.save(pb2.DataTransferEntry(key=key, text=text))
    except Exception:
        handle_error("Unable to save data on this node")
    else:
        print(response.message)
def find(key):
    global node_channel, node_stub
    
    if node_channel is None:
        print("Not connected to the node")
        return
    try:
        response = node_stub.find(pb2.TextMessage(text=key))
    except Exception:
        handle_error("Unable to search for the data on the node")
    else:
        print(response.message)

def remove(key):
    global node_channel, node_stub
    
    if node_channel is None:
        print("Not connected to the node")
        return
    try:
        response = node_stub.remove(pb2.TextMessage(text=key))
    except Exception:
        handle_error("Unable to remove data from this node")
    else:   
        print(response.message)

def quit():
    print("Shutting client down")
    exit(0)

if debug:
    connect(debug_node)
    save("24")
    save("25")
    save("26")

while True:
    try:
        command = input()
        if match := re.search(connect_regex, command):
            connect(match.group(0).split()[1])
        elif match := re.search(get_info_regex, command):
            get_info()
        elif match := re.search(save_regex, command):
            save(match.group(1), match.group(2))
        elif match := re.search(find_regex, command):
            find(match.group(0).split()[1])
        elif match := re.search(remove_regex, command):
            remove(match.group(0).split()[1])
        elif match := re.search(quit_regex, command):
            quit()
    except KeyboardInterrupt:
        quit()