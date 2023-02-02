import random
import re
import sys
import grpc
import queue_pb2 as pb2
import queue_pb2_grpc as pb2_grpc

# P.S. this is working not as intended and was written napohui without additional checks

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
stub = pb2_grpc.NewQueueServiceStub(channel)

put_regex = re.compile("(?<=^put ).*$")
peek_regex = re.compile("peek")
pop_regex = re.compile("pop")
size_regex = re.compile("size")


while True:
    try:
        req = input().strip()
        if match := re.search(put_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Put(msg)
            print(response.text)
        elif match := re.search(peek_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Peek(msg)
            print(response.text)
        elif match := re.search(pop_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Pop(msg)
            print(response.text)
        elif match := re.search(size_regex, req):
            msg = pb2.TextMessage(message=match.group(0))
            response = stub.Size(msg)
            print(response.text)
        else:
            print("No matching command found")
    except KeyboardInterrupt:
        print("Shutting client down")
