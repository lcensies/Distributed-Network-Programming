#!/usr/bin/python3
import signal
import sys
from multiprocessing import Queue
import socket
from threading import Thread

if len(sys.argv) > 1:
    serv_port = int(sys.argv[1])
else:
    serv_port = 3535

serv_addr = ("localhost", serv_port)
# run_threads = True

def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True

def process_list(i_thread, client):
    conn, addr = client[0], client[1]
    print(f"Thread {i_thread} started working with {addr}")
    while True:
        data = conn.recv(1024)
        if not data:
            print(f"Session with client {addr} which was handled by thread {i_thread} is terminated.")
            return
        num = data.strip().decode("ascii")
        if not num.isdigit():
            print(f"Invalid number format - {num}. Expected integer.")
            continue
        ans = str(is_prime(int(num)))
        # print(f"{addr} - {num} - {ans}")
        conn.sendall(ans.encode("ascii"))

def start_worker(i_thread):
    # global run_threads
    print(f"Thread {i_thread} is looking for pending requests.")
    # while run_threads:
    while True:
        try:
            client = q.get(block=True)
            # client = q.get(block=True, timeout=2)
            process_list(i_thread, client)
        except Exception as e:
            continue
    print(f"Stopping thread {i_thread}")

def handle_stop_signals(signum, frame):
    # global run_threads
    # run_threads = False
    print("Terminating the program.")
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
    print(f"Main thread accepted connection from {addr}")
    q.put((conn, addr))
