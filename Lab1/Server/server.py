import os
import random
import socketserver
import string
import threading
import traceback
from math import ceil

from pathvalidate import sanitize_filepath, sanitize_filename
import redis

debug = True

# server_address = ("", 3434)
server_address = ("127.0.0.1", 3434)
server_secret = ''.join(random.choice(string.ascii_lowercase) for i in range(5))

# recv_chunk_size = 32
# buf_size = recv_chunk_size * 2

buf_size = 1024


script_dir = os.path.abspath(os.path.dirname(__file__))
files_dir = os.path.join(script_dir, "Files")
# r = redis.Redis(host='localhost', port=9999)
# r.mset({"Croatia": "Zagreb", "Bahamas": "Nassau"})
# print(r.get("Bahamas"))

session_storage = {}


def parse_message(datagram):
    
    message = {}

    if chr(datagram[0]) == "s":
        
        # Separate message on 3 groups maximum
        splitted = datagram.split(b" | ", 3)
        
        message["type"] = "start"
        
        seq_no = splitted[1].decode("ascii")
        
        if not (seq_no.isdigit() and int(seq_no) >= 0):
            raise ValueError(f"Invalid sequence number {splitted[1]}")


        message["seq_no"] = int(seq_no)
        
        # In order to prevent directory traversing 
        message["filename"] = sanitize_filename(splitted[2].decode("ascii"))

        if not splitted[3].isdigit():
            raise ValueError(f"Invalid format of total size {splitted[2]}. Expected integer.")


        message["total_size"] = int(splitted[3])

    elif chr(datagram[0]) == "d":

        # Separate message on 2 groups maximum
        splitted = datagram.split(b" | ", 2)
        
        message["type"] = "data"
        
        seq_no = splitted[1].decode("ascii")
        
        if not (seq_no.isdigit() and int(seq_no) >= 0):
            raise ValueError(f"Invalid sequence number {seq_no}")

        message["seq_no"] = int(seq_no)
        
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
        bytes = b''.join(session_storage[sid]["chunks"])
        
        filepath = os.path.join(files_dir, session_storage[sid]["filename"])
        
        with open(filepath, "wb") as f:
            f.write(bytes)
        
        print(f"Saved file {session_storage[sid]['filename']}")
    
    def get_sid(self):
        return self.client_address[0] + str(self.client_address[1]) + server_secret
    
    def handle_start(self, message, sid):
        session = self.init_session(message)
        session_storage[sid] = session

        print(f'Received start message from {self.client_address}: {message}')
        
        message = f'a | {session["seq_no"] + 1} | {buf_size}'
        
        self.wfile.write(message.encode())
        
        print(f'Sent start ack message {message}')
        
        
    def handle_data(self, message, sid):
        if sid not in session_storage:
            raise Exception("Client is sending data message without preceding start")

        seq_no = message["seq_no"]

        if seq_no not in range(0, session_storage[sid]['n_chunks'] + 1):
            raise Exception(f"Invalid sequence number. Expected [0, {session_storage[sid]['n_chunks']}]. Got: {seq_no}")
        

        if seq_no > 0 and session_storage[sid]["chunks"][seq_no - 1] is not None:
            raise Exception(f"Duplicate chunk with sequence number {seq_no} received") 
        session_storage[sid]["chunks"][seq_no - 1] = message["data_bytes"]
        
        message = f'a | {seq_no + 1}'
        self.wfile.write(message.encode())
        print(f"Sent data ack message {message}")
        
        if seq_no == session_storage[sid]["n_chunks"]:
            self.save_file(sid)
        
        
    def handle(self):

        print("Recieved one request from {}".format(self.client_address))
        
        # bytes = self.rfile.readline()
        
        # If client will send more data than buf_size, server would read only buf_size
        bytes = self.rfile.read()
        datagram = bytes
        # datagram = bytes.strip()
        print(f"Datagram Recieved from client is: {datagram}")

        try:
            message = parse_message(datagram)
        except Exception as e:
            print(e)
            if debug:
                traceback.print_exc()
            return

        try:
            if message["type"] == "start":
                ret = self.handle_start(message, self.get_sid())
            elif message["type"] == "data":
                ret = self.handle_data(message, self.get_sid())
        except Exception as e:
            print(e)
            if debug:
                traceback.print_exc()
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

# TODO split only by fist 2 dashes

# TODO read only specified size

# TODO at last seq_no check if all data is present

# TODO fix duplicates correct handling

# Split by first N ocurrences https://stackoverflow.com/questions/6903557/splitting-on-first-occurrence