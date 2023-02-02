import sys
from concurrent import futures
from threading import Lock
import queue_pb2_grpc as pb2_grpc
import queue_pb2 as pb2
import grpc
import queue

# P.S. this is working not as intended and was written napohui without additional checks

q_lock = Lock()
q_size = 10

if len(sys.argv) > 2:
    serv_addr = f"localhost:{sys.argv[1]}"
    q_size = int(sys.argv[2])
else:
    serv_addr = "localhost:5555"

q = queue.Queue(maxsize=q_size)

class QueueHandler(pb2_grpc.NewQueueServiceServicer):
    def Put(self, request, context):
        try:
            q.put(request.message, block=False)
            ret = "True"
        except queue.Full:
            ret = "False"
        return pb2.Response(status_code=0, text=ret)
    
    def Peek(self, request, context):
        with q_lock:
            if q.qsize() == 0:
                status_code = -1
                text = "None"
            else:
                status_code = 0
                text = q.queue[0]
                
        response = pb2.Response(status_code=status_code, text=text)
        
        return response
        
    def Pop(self, request, context):
        if q.qsize() == 0:
            status_code = -1
            text = "None"
        else:
            status_code = 0
            text = q.get()
        response = pb2.Response(status_code=status_code, text=text)
        return response
    def Size(self, request, contex):
        return pb2.Response(status_code=0, text=str(q.qsize()))

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb2_grpc.add_NewQueueServiceServicer_to_server(QueueHandler(), server)
server.add_insecure_port(serv_addr)

server.start()
print(f"Server started")
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print("Shutting server down")
