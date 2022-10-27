#!/usr/bin/python3
import signal
import sys
from multiprocessing import Queue
import socket
from threading import Thread, Lock
import hashlib

if len(sys.argv) > 1:
    serv_port = int(sys.argv[1])
else:
    serv_port = 5555

serv_addr = ("", serv_port)

session_storage = {}
session_storage_mutex = Lock()

def print_sessions(str_in: str):
    with session_storage_mutex:
        sessions = ' '.join(sorted(session_storage.values())) + '\n' 
    return sessions

def start_processing(i_thread, client):
    conn, addr = client[0], client[1]
    while True:
        data = conn.recv(1024)
        if not data:
            print(f"Client disconnected")
            with session_storage_mutex:
                if str(addr) in session_storage:
                    del session_storage[str(addr)]
            
            return
        
        name = data.strip().decode("utf-8")
        
        if str(addr) not in session_storage:
            with session_storage_mutex:
                session_storage[str(addr)] = name
        
        ans = str(print_sessions(name))
        conn.sendall(ans.encode("utf-8"))

# def start_worker(i_thread):
#     while True:
#         try:
#             client = q.get(block=True)
#             start_processing(i_thread, client)
#         except Exception as e:
#             continue
#     print(f"Stopping thread {i_thread}")

def handle_stop_signals(signum, frame):
    print("Server is stopped.")
    sys.exit(0)

n_threads = 30
q = Queue()

# threads = [Thread(target=start_worker, args=(i,), daemon=True) for i in range(n_threads)]
# [t.start() for t in threads]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(serv_addr)
server.listen()

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)


while True:
    conn, addr = server.accept()
    q.put((conn, addr))

