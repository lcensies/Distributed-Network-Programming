#! /usr/bin/env python3
import os
import socket
import select
import sys
import traceback
from tenacity import retry, stop_after_attempt, retry_if_result, RetryError, wait_fixed

debug = False
usage = f"Usage: python3 server_ip:port src_filename dst_filename"

# client_addr = ('', 9000)
client_addr = ('localhost', 9000)

client_bufsize = 4096
start_seqno = 0
max_retries = 5
retry_timeout = 3  # in seconds

if len(sys.argv) > 1:
    server_addr = sys.argv[1].split(":")
    server_addr = (server_addr[0], int(server_addr[1]))
else:
    # server_addr = ('localhost', 3434)
    print(usage)
    exit()

if len(sys.argv) > 2:
    src_filename = sys.argv[2]
else:
    # src_filename = "Client/Files/enum.txt"
    print(usage)
    exit()

if len(sys.argv) > 3:
    dst_filename = sys.argv[3]
else:
    # dst_filename = "enum.txt"
    print(usage)
    exit()

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setblocking(0)
client.bind(client_addr)

class InvalidSeqnoException(Exception):
    pass

def parse_init_ack(datagram, params=None):
    splitted = datagram.split(" | ")

    if not len(splitted) == 3:
        raise Exception(f"Wrong number of parameters. Expected 3. Got {len(splitted)}")

    if not (splitted[1].isdigit() and int(splitted[1]) == start_seqno + 1):
        raise Exception(f"Invalid sequence number. Expected {start_seqno + 1}. Got {splitted[1]}")

    if not (splitted[2].isdigit() and int(splitted[2]) in range(1, 65527)):
        raise Exception(f"Invalid buffer size. Expected integer in range [1, 65527]. Got {splitted[2]}")
    
    print(f"Buffer size selected by the server: {splitted[2]}")
    
    return {
        "type": "ack",
        "next_seqno": int(splitted[1]),
        "buf_size": int(splitted[2])
    }
def parse_data_ack(datagram, params):
    splitted = datagram.split(" | ")

    if not len(splitted) == 2:
        raise Exception("Wrong number of parameters. Expected 2")
    if not (splitted[1].isdigit()):
        raise TypeError(f"Invalid sequence number type. Expected integer.")
    
    seq_no = params["seq_no"]
    next_seqno = int(splitted[1])
    
    if not (next_seqno == seq_no + 1):
        raise InvalidSeqnoException(f"Invalid sequence number received. Expected {seq_no+1}")
    
    return {
        "type": "ack",
        "next_seqno": next_seqno
    }

@retry(stop=stop_after_attempt(max_retries), retry=retry_if_result(lambda x: x is None), wait=wait_fixed(0.15), reraise=True)
def send_message(message, callback, params=None):

    client.sendto(message, server_addr)
    ready = select.select([client], [], [], retry_timeout)
    if not ready[0]:
        return None

    data = client.recv(client_bufsize).decode("ascii")
    if data == "":
        return None

    return callback(data, params)
def send_file(src_filename, dst_filename):
    # client.sendto(message, server_addr) 
    
    try:
        f = open(src_filename, 'rb')
        
    except FileNotFoundError:
        print(f"File {src_filename} is not found. Exiting.")
        return
    try:
        total_size = os.stat(src_filename).st_size
        seq_no = start_seqno
        message = f"s | {seq_no} | {dst_filename} | {total_size}".encode("ascii")
        ack = send_message(message, parse_init_ack)
        seq_no = ack["next_seqno"]
        server_bufsize = ack["buf_size"]
        message_header = f"d | {seq_no} | "
        message_data_size = server_bufsize - len(message_header)
        
        while (data := f.read(message_data_size)):
            message = message_header.encode("ascii") + data
            ack = send_message(message, parse_data_ack, params={"seq_no": seq_no})
            
            seq_no = ack["next_seqno"]
            message_header = f"d | {seq_no} | "
            message_data_size = server_bufsize - len(message_header)
        
        if ack is not None:
            print(f"Successfully sent file {src_filename} to the server")
            
    except Exception as e:
        if type(e) == RetryError:
            print(f"Exceeded maximum number of retries {max_retries}")
        print(e)
        if debug:
            traceback.print_exc()

print(f"Trying to send {src_filename} to {server_addr}")
send_file(src_filename, dst_filename)