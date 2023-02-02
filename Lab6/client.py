import random
import re
import sys
import grpc
import raft_pb2 as pb2
import raft_pb2_grpc as pb2_grpc

debug = False
debug_node = "127.0.0.1:50000"

msg = pb2.TextMessage(text="")

connect_regex = re.compile("^connect .*$")
get_leader_regex = re.compile("^getleader$")
suspend_regex = re.compile("^suspend \d+(\.\d*)?$")
quit_regex = re.compile("^quit$")


server_channel, server_stub, server_type = None, None, None
node_channel, node_stub = None, None

print("Client is started")


class NodeRepr:
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return f"{self.node.id}\t{self.node.address.ip}:{self.node.address.port}"


def handle_error(message: str):
    global node_channel, node_stub

    print(message)

    if node_channel is not None:
        print("Assuming node is dead. Closing RPC channel")
        node_channel.close()
    # 
    # server_channel, server_stub, server_type = None, None, None
    # node_channel, node_stub = None, None


def connect(remote_addr):
    global msg, node_stub, node_channel

    if node_channel is not None:
        node_channel.close()

    node_channel = grpc.insecure_channel(remote_addr)
    node_stub = pb2_grpc.RaftServerStub(node_channel)


def get_leader():
    global node_channel, node_stub, msg
    if node_channel is None:
        print("Not connected to any kind of server")
        return
    try:
        response = node_stub.GetLeader(msg)
    except Exception as e:
        handle_error("Unable to get leader.")
    else:
        if response.id != -1:
            print(f"Node's leader is id:{response.id} addr:{response.address}")
        else:
            print(f"Node has no leader")
def suspend(period=1):
    global node_channel, node_stub

    if node_channel is None:
        print("Not connected to the node")
        return
    try:
        response = node_stub.Suspend(pb2.TextMessage(text=period))
    except Exception:
        pass
    finally:
        print(f"Sent signal to suspend node for {period} seconds")

def quit():
    print("Shutting client down")
    exit(0)


if debug:
    connect(debug_node)

while True:
    try:
        command = input()
        if match := re.search(connect_regex, command):
            connect(match.group(0).split()[1])
        elif match := re.search(suspend_regex, command):
            suspend(match.group(0).split()[1])
        elif match := re.search(get_leader_regex, command):
            get_leader()
        elif match := re.search(quit_regex, command):
            quit()
    except KeyboardInterrupt:
        quit()
