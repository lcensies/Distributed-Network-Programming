# DNP lab 5

- Install gRPC
```bash
pip3 install grpcio grpcio-tools
```

- Compile .proto
```bash
python3 -m grpc_tools.protoc chord.proto --proto_path=. --python_out=. --grpc_python_out=.
```

## Testing

- [X] Node successfully connects to the chord if registry is available
- [X] Node prints the error message and terminates if there are no free spots left in the chord 
- [X] Node correctly updates it's fingertable every 1 second
- [X] Node correctly inherits data from it's successor when it joins chord
- [X] Node quits the chord correctly
  - [X] Data is passed to the successor
  - [X] Registry is notified that node is about to leave and removes it from the list
- [X] Client can connect to the registry and get information about the chord
- [X] Client can connect to the node and get information about it's fingertable
- [X] save, find, delete methods are working correctly if node is responsible for the key
- [X] Error messages are returned for save, find, delete methods in corresponding situations
  - [X] Key is unavailable
  - [X] Server side errors handling
- [X] Successor and predecessor pointers at corresponding nodes are updated when new node joins the chord
- [X] Node can delegate save, find, delete requests to other node if it's not responsible for the key
- [X] Save method
  - [X] 1. Only 1 node in the chord
  - [X] 2. Two nodes in the chord
- [X] Find method
- [X] Delete method
