import grpc
import SimpleService_pb2 as pb2
import SimpleService_pb2_grpc as pb2_grpc

channel = grpc.insecure_channel(f"127.0.0.1:5555")
stub = pb2_grpc.SimpleServiceStub(channel)

msg = pb2.Message(message="Hello there!")
response = stub.GetServerResponse(msg)

print(response)
print(response.received)
print(response.message)