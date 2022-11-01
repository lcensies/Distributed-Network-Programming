```bash
pip3 install grpcio grpcio-tools
```

```bash
python3 -m grpc_tools.protoc SimpleService.proto --proto_path=. --python_out=. --grpc_python_out=.
```

- SimpleService_pb2.py 
  - Serialization and message parsing logic

- SimpleService_pb2_grpc.py
  - Stub for request handler
  - Stub for client

