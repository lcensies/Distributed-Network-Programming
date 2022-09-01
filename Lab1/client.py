#! /usr/bin/env python3
import argparse
import socket
import sys

server_addr = sys.argv[1] if len(sys.argv) > 1 else 'localhost:3434'
server_ip, server_port = server_addr.split(":")[0], int(server_addr.split(":")[1])
server_addr = (server_ip, server_port)

def send_file():

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for _ in range(5):

        message = str(_).encode("ascii")
        client.sendto(message, server_addr)
        response = client.recv(1 << 12).decode('ascii')
        print(response)

send_file()





