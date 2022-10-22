import random
import re
import sys
import grpc
import QueueService_pb2 as pb2
import QueueService_pb2_grpc as pb2_grpc


debug = False

if len(sys.argv) > 2 and sys.argv[2].isdigit():
    debug = True
    serv_addr = sys.argv[1]
    n_nums = int(sys.argv[2])
elif len(sys.argv) > 1:
    serv_addr = sys.argv[1]
else:
    serv_addr = "localhost:5555"


channel = grpc.insecure_channel(serv_addr)
stub = pb2_grpc.QueueServiceStub(channel)

put_regex = re.compile("(?<=^put ).*$")
pick_regex = re.compile("pick")
pop_regex = re.compile("pop")
size_regex = re.compile("size")


while True:
    try:
        req = input().strip()
        if match := re.search(put_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Put(msg)
            if response.status_code == 0:
                print(f"Element was added to the queue")
            else:
                print(response.text)
        elif match := re.search(pick_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Pick(msg)
            if response.status_code == 0:
                print(f"Element is {response.text}")
            else:
                print(response.text)
        elif match := re.search(pop_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Pop(msg)
            if response.status_code == 0:
                print(f"Element is {response.text}")
            else:
                print(response.text)
        elif match := re.search(size_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Size(msg)
            if response.status_code == 0:
                print(f"Size is {response.text}")
            else:
                print(response.text)
        else:
            print("No matching command found")
    except KeyboardInterrupt:
        print("Shutting client down")
