```bash
python3 -m grpc_tools.protoc raft.proto --proto_path=. --python_out=. --grpc_python_out=.
```

- Kill all python processes
```bash
ps -e | grep python | cut -d ' ' -f 2 | tr '\n' ' ' | xargs kill
```

