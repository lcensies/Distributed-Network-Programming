import random
import socketserver
import string
import threading
from math import ceil

from pathvalidate import sanitize_filepath, sanitize_filename
import redis

server_address = ("127.0.0.1", 3434)
server_secret = ''.join(random.choice(string.ascii_lowercase) for i in range(5))

recv_chunk_size = 32
buf_size = recv_chunk_size * 2

# r = redis.Redis(host='localhost', port=9999)
# r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
# print(r.get("Bahamas"))

session_storage = {}


def parse_message(datagram):
    splitted = str(datagram).split(" | ")
    message = {}

    if splitted[0] == "s":

        message["type"] = "start"

        if not (splitted[1].isdigit() and int(splitted[1]) >= 0):
            raise ValueError("Invalid sequence number")

        message["seq_no"] = int(splitted[1])

        message["filename"] = sanitize_filename(splitted[2])

        if not splitted[3].isdigit():
            raise ValueError("Invalid total size")

        message["total_size"] = int(splitted[3])

    elif splitted[0] == "d":

        message["type"] = "data"

        if not splitted[1].isdigit():
            raise ValueError("Invalid sequence number")

        message["seq_no"] = int(splitted[1])

        message["data_bytes"] = splitted[2]
    else:
        raise Exception('Unsupported message type')

    return message


# filename | total_size

class MyUDPRequestHandler(socketserver.DatagramRequestHandler):

    def restore_session(self, sid):

        if sid in session_storage:
            return session_storage[sid]
        else:
            return None

    def init_session(self, message):

        sid = self.get_sid()

        session_storage[sid] = {
            "seq_no": message["seq_no"],
            "filename": message["filename"],
            "total_size": message["total_size"],
            "n_chunks":  ceil(int(message["total_size"]) / buf_size),
            "chunks": [None] * ceil(int(message["total_size"]) / buf_size)
        }

        return session_storage[sid]
    
    def save_file(self, sid):
        bytes = str.encode(''.join(session_storage[sid]["chunks"]))
    
        with open(session_storage[sid]["filename"], "wb") as f:
            f.write(bytes)
        
        print(f"Saved file {session_storage[sid]['filename']}")     
    
    def get_sid(self):
        return self.client_address[0] + str(self.client_address[1]) + server_secret
    
    def handle_start(self, message, sid):
        session = self.init_session(message)
        session_storage[sid] = session
        self.wfile.write(f'a | {session["seq_no"] + 1} | {buf_size}'.encode())

        print(f'Received start message from {self.client_address}: {message}')
        
    def handle_data(self, message, sid):
        if sid not in session_storage:
            raise Exception("Client is sending data message without preceding start")

        seq_no = message["seq_no"]

        if seq_no > session_storage[sid]["n_chunks"] + 1:
            raise Exception(f"Invalid sequence number. Expected [0, {session_storage[sid]['n_chunks'] + 1}]. Got: {seq_no}")
    
        session_storage[sid]["chunks"][seq_no - 1] = message["data_bytes"]

        self.wfile.write(f'a | {seq_no + 1}'.encode())
        
        if seq_no == session_storage[sid]["n_chunks"]:
            self.save_file(sid)
        
        
    def handle(self):

        print("Recieved one request from {}".format(self.client_address))
        
        # bytes = self.rfile.readline()
        bytes = self.rfile.read()
        datagram = bytes.strip().decode("ascii")
        print(f"Datagram Recieved from client is: {datagram}")

        try:
            message = parse_message(datagram)
        except Exception as e:
            print(e)
            return

        try:
            if message["type"] == "start":
                ret = self.handle_start(message, self.get_sid())
            elif message["type"] == "data":
                ret = self.handle_data(message, self.get_sid())
        except Exception as e:
            print(e)
            return

        # print(datagram)

        # print("Thread Name:{}".format(threading.current_thread().name))

        # self.wfile.write("Message from Server! Hello Client".encode())


server = socketserver.ThreadingUDPServer(server_address, MyUDPRequestHandler)
print(f"Server is listening on {server_address}")
server.serve_forever()

# no session, start -> initial messagee
# no session, data -> malicious client, ignore
# session, data -> filetransfer
# session, start -> malfunctioning client / ack message was lost -> reinitialize session


# Note that data chunks are stored and assembled in the memory

# Timers https://docs.python.org/3/library/threading.html#timer-objects

# TODO check for data validity
# TODO duplicates handling

# TODO directory traversal avoidance

# TODO some encoding for bytes?