import SimpleService_pb2_grpc as pb2_grpc
import grpc
from concurrent import futures

from Lab4.Example.simple_handler import SimpleHandler

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb2_grpc.add_SimpleServiceServicer_to_server(SimpleHandler(), server)
server.add_insecure_port("127.0.0.1:5555")
server.start()
print(f"Server started")
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print("Shutting server down")
