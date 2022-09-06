#! /usr/bin/env python3
import argparse
import os
import socket
import select
import sys
from math import ceil
from tenacity import retry, stop_after_attempt, retry_if_exception_type
import chardet

client_addr = ('localhost', 9000)
server_addr = sys.argv[1] if len(sys.argv) > 1 else ('localhost', 3434)

client_bufsize = 4096
start_seqno = 0
max_retries = 5
retry_timeout = 500  # in seconds

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.setblocking(0)
client.bind(client_addr)

class InvalidSeqnoException(Exception):
    pass

def parse_init_ack(datagram):
    splitted = datagram.split(" | ")

    if not len(splitted) == 3:
        raise Exception(f"Wrong number of parameters. Expected 3. Got {len(splitted)}")

    if not (splitted[1].isdigit() and int(splitted[1]) == start_seqno + 1):
        raise Exception(f"Invalid sequence number. Expected {start_seqno + 1}. Got {splitted[1]}")

    if not (splitted[2].isdigit() and int(splitted[2]) in range(1, 65527)):
        raise Exception(f"Invalid buffer size. Expected integer in range [1, 65527]. Got {splitted[2]}")

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

# @retry(stop=stop_after_attempt(max_retries), retry=retry_if_exception_type())
# def send_request(message, callback, params=None):
#     client.sendto(message, server_addr)
#     ready = select.select([client], [], [], retry_timeout)
# 
#     for i in range(max_retries):
#         if not ready[0]:
#             continue
# 
#         data = client.recv(client_bufsize).decode("ascii")
#         if not data:
#             return None
# 
#         return callback(data, params)
# 
#     return None

@retry(stop=stop_after_attempt(max_retries), reraise=True)
def send_start(dst_filename, total_size):
    message = f"s | {start_seqno} | {dst_filename} | {total_size}".encode()
    client.sendto(message, server_addr)
    # response = client.recv(4096).decode('ascii')
    ready = select.select([client], [], [], retry_timeout)

    for i in range(max_retries):
        if not ready[0]:
            continue

        data = client.recv(client_bufsize).decode()
        if not data:
            return None

        return parse_init_ack(data)

    return None

@retry(stop=stop_after_attempt(max_retries), reraise=True)
def send_chunk(seq_no, data_bytes):
    message = f"d | {seq_no} | ".encode() + data_bytes
    
    # message = f"d | {seq_no} | {data_bytes}".encode()
    client.sendto(message, server_addr)
    ready = select.select([client], [], [], retry_timeout)
    
    for i in range(max_retries):
        if not ready[0]:
            continue

        data = client.recv(client_bufsize).decode()
        if not data:
            return None
        
        return parse_data_ack(data, params={"seq_no": seq_no})
    
    return None


def send_file(src_filename, dst_filename):
    # client.sendto(message, server_addr) 
    
    try:
        f = open(src_filename, 'rb')
        
    except FileNotFoundError:
        print("File is not found. Exiting.")
        return
    try:
        total_size = os.stat(src_filename).st_size
        seq_no = start_seqno
        # message = f"s | {seq_no} | {dst_filename} | {total_size}".encode("ascii")
        # ack = send_message(message, parse_init_ack)
        ack = send_start(dst_filename, total_size)
        # next_seqno = ack["next_seqno"]
        server_bufsize = ack["buf_size"]
        
        chunks = [None] * ceil(total_size / server_bufsize) 
        
        for i in range(len(chunks)):
            chunks[i] = f.read(server_bufsize)
            seq_no = ack["next_seqno"]
            # message = f"d | {seq_no} | {chunks[i]}"
            # ack = send_message(message, parse_data_ack, params={"seq_no": seq_no})
            ack = send_chunk(seq_no, chunks[i])
            
    except Exception as e:
        print(e)
            # client.sendto(message, server_addr)
            # # response = client.recv(4096).decode('ascii')
            # ready = select.select([client], [], [], retry_timeout)

# while (l):
#     conn.send(l)
#     l = output.read(1024)
# output.close()
#         
#     except Exception as e:
#         print(e)
#         return
#     
#     f.close()




# src_filename = "Client/test_file.txt"
src_filename = "Client/photo.jpg"
dst_filename = src_filename

send_file(src_filename, dst_filename)

# s | seqno 0 | filename | total_size

# Is data handling correct?
# Improvements: decorators, parallel sending
# https://stackoverflow.com/questions/52599656/how-to-send-files-in-chunks-by-socket
# https://stackoverflow.com/questions/2719017/how-to-set-timeout-on-pythons-socket-recv-method

# Retry exception https://tenacity.readthedocs.io/en/latest/

# TODO if ack == None ack = send_start(dst_filename, total_size)

# TODO wipe session 