import os
import random
import socketserver
import string
import sys
import threading
import traceback
from pathvalidate import sanitize_filename

debug = False
permanent_sessions = False

# server_address = ("", 3434)
if len(sys.argv) > 1:
    server_addr = sys.argv[1].split(":")
    server_addr = (server_addr[0], int(server_addr[1]))
else:
    server_address = ("localhost", 3434)
    
# Server secret will be used for session identifiers generation
server_secret = ''.join(random.choice(string.ascii_lowercase) for i in range(10))

# By default, max buf_size for the ThreadingUDPServer is 8192
buf_size = 1024


script_dir = os.path.abspath(os.path.dirname(__file__))
# files_dir = os.path.join(script_dir, "Files")
files_dir = script_dir

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


class Server(socketserver.DatagramRequestHandler):
    def remove_session(self, sid):
        if permanent_sessions:
            return
        if sid not in session_storage:
            return
        print(
            f"Client with sid {sid} is inactive for {session_storage[sid]['timer'].interval} seconds. Removing session.")
        return session_storage.pop(sid, None)

    def restore_session(self, sid):
        if sid in session_storage:
            return session_storage[sid]
        else:
            return None

    def init_session(self, message):

        sid = self.get_sid()

        session_storage[sid] = {
            "seq_no": message["seq_no"],
            'start_seqno': message["seq_no"],
            "filename": message["filename"],
            "bytes_received": 0,
            "total_size": message["total_size"],
            "chunks": []
        }

        return session_storage[sid]

    def save_file(self, sid):
        bytes = b''.join(session_storage[sid]["chunks"])
        filepath = os.path.join(files_dir, session_storage[sid]["filename"])

        with open(filepath, "wb") as f:
            f.write(bytes)

        print(f"Saved file {session_storage[sid]['filename']}")
    
    # Not optimal way to obtain current session identifier
    def get_sid(self):
        return self.client_address[0] + str(self.client_address[1]) + server_secret

    def handle_start(self, message, sid):
        # Start new session
        session = self.init_session(message)
        session_storage[sid] = session

        print(f'Received start message from {self.client_address}: {message}')

        message = f'a | {session["seq_no"] + 1} | {buf_size}'

        self.wfile.write(message.encode())

        # Remove session if client is inactive for 3 seconds
        session_storage[sid]["timer"] = threading.Timer(3.0, self.remove_session, args=[sid])
        session_storage[sid]["timer"].start()

        print(f'Sent start ack message {message}')

    def handle_data(self, message, sid):
        if sid not in session_storage:
            raise Exception("Data message for inexistent sid was sent.")

        session_storage[sid]["timer"].cancel()

        seq_no = message["seq_no"]

        start_seqno = session_storage[sid]['start_seqno']

        if seq_no <= start_seqno:
            raise Exception(f"Invalid sequence number {seq_no}")

        session_storage[sid]["seq_no"] = seq_no

        chunk_ind = seq_no - session_storage[sid]["start_seqno"] - 1
        chunks_received = len(session_storage[sid]["chunks"])
        
        # Appending new file chunk to the array. 
        # Not optimal way to handle files, especially if file size is large.
        if chunks_received == chunk_ind:
            session_storage[sid]["chunks"].append(message["data_bytes"])
            session_storage[sid]["bytes_received"] += len(message["data_bytes"])
        else:
            print(f"Duplicate chunk with sequence number {seq_no} is received")

        message = f'a | {seq_no + 1}'
        self.wfile.write(message.encode())

        print(f"Sent data ack message {message}")

        if session_storage[sid]["bytes_received"] == session_storage[sid]["total_size"]:
            self.save_file(sid)
            session_storage[sid]["timer"] = threading.Timer(1.0, self.remove_session, args=[sid])
            session_storage[sid]["timer"].start()
        elif not permanent_sessions:
            session_storage[sid]["timer"] = threading.Timer(3.0, self.remove_session, args=[sid])
            session_storage[sid]["timer"].start()

    def handle(self):
        # print("Recieved one request from {}".format(self.client_address))

        datagram = self.rfile.read(buf_size)
        # print(f"Datagram Recieved from client is: {datagram}")

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

            if self.get_sid() not in session_storage:
                return

            session_storage[self.get_sid()]["timer"] = threading.Timer(3.0, self.remove_session, args=[self.get_sid()])
            session_storage[self.get_sid()]["timer"].start()

server = socketserver.ThreadingUDPServer(server_address, Server)
print(f"Server is listening on {server_address}")
server.serve_forever()


