import sys

import service_pb2_grpc as pb2_grpc
import service_pb2 as pb2
import grpc
from concurrent import futures

if len(sys.argv) > 1:
    serv_addr = sys.argv[1]
else:
    serv_addr = "localhost:5555"


def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True

class RequestHandler(pb2_grpc.ServiceServicer):
    def ReverseText(self, request, context):
        msg = request.message
        reply = {"message": msg[::-1]}
        # reply = {"message": msg, "received": True}
        return pb2.ReverseTextMessageResponse(**reply)
    def SplitText(self, request, context):
        msg = request.message
        splitted = msg.split(request.delim)
        reply = pb2.SplitTextMessageResponse()
        reply.parts.extend(splitted)
        reply.n_parts = len(splitted)
        return reply
    
    def GetIsPrimeStream(self, request_iterator, context):
        for req in request_iterator:
            print(f"Request: {req}")
            ans = is_prime(req.num)
            if ans == True:
                res = f"{req.num} is prime"
            else:
                res = f"{req.num} is not prime"
            yield pb2.TextMessage(message=res)



server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb2_grpc.add_ServiceServicer_to_server(RequestHandler(), server)
server.add_insecure_port(f"{serv_addr}")

server.start()
print(f"Server started")
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print("Shutting server down")
