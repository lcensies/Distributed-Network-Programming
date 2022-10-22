import sys
from concurrent import futures
from threading import Lock
import QueueService_pb2 as pb2
import QueueService_pb2_grpc as pb2_grpc
import grpc
import queue

q = queue.Queue()
q_lock = Lock()

if len(sys.argv) > 1:
    serv_addr = sys.argv[1]
else:
    serv_addr = "localhost:5555"


class QueueHandler(pb2_grpc.QueueServiceServicer):
    def Put(self, request, context):
        q.put(request.message)
        return pb2.Response(status_code=0, text="")
    
    def Pick(self, request, context):
        with q_lock:
            if q.qsize() == 0:
                status_code = -1
                text = "Queue is empty"
            else:
                status_code = 0
                text = q.queue[0]
                
        response = pb2.Response(status_code=status_code, text=text)
        
        return response
        
    def Pop(self, request, context):
        if q.qsize() == 0:
            status_code = -1
            text = "Queue is empty"
        else:
            status_code = 0
            text = q.get()
        response = pb2.Response(status_code=status_code, text=text)
        return response
    def Size(self, request, contex):
        return pb2.Response(status_code=0, message=q.qsize())

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb2_grpc.add_QueueServiceServicer_to_server(QueueHandler(), server)
server.add_insecure_port(f"{serv_addr}")

server.start()
print(f"Server started")
try:
    server.wait_for_termination()
except KeyboardInterrupt:
    print("Shutting server down")
