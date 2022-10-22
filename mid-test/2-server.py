#!/usr/bin/python3
import signal
import sys
from multiprocessing import Queue
import socket
from threading import Thread
import hashlib

if len(sys.argv) > 1:
    serv_port = int(sys.argv[1])
else:
    serv_port = 50505

serv_addr = ("localhost", serv_port)
# run_threads = True

session_storage = {}

def calc_hash(str_in: str):
    return hashlib.md5(str_in.encode('utf-8')).hexdigest()

def start_processing(i_thread, client):
    conn, addr = client[0], client[1]
    print(f"Thread {i_thread} started working with {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            print(f"Client disconnected")
            return
        num = data.strip().decode("utf-8")
        ans = str(calc_hash(num))
        # print(f"{addr} - {num} - {ans}")
        conn.sendall(ans.encode("utf-8"))

def start_worker(i_thread):
    print(f"Thread {i_thread} is looking for pending requests.")
    while True:
        try:
            client = q.get(block=True)
            start_processing(i_thread, client)
        except Exception as e:
            continue
    print(f"Stopping thread {i_thread}")

def handle_stop_signals(signum, frame):
    print("Server is stopped.")
    sys.exit(0)

n_threads = 10
# q = Queue(maxsize=n_threads)
q = Queue()

threads = [Thread(target=start_worker, args=(i,), daemon=True) for i in range(n_threads)]
[t.start() for t in threads]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(serv_addr)
server.listen()

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)


while True:
    conn, addr = server.accept()
    # print(f"Main thread accepted connection from {addr}")
    q.put((conn, addr))

