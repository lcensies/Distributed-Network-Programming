#!/usr/bin/python3
import socket
import sys

if len(sys.argv) > 1:
    serv_addr = sys.argv[1].split(":")
    serv_addr = (serv_addr[0], int(serv_addr[1]))
else:
    serv_addr = ("localhost", 3535)

numbers = [15492781, 15492787, 15492803,
           15492811, 15492810, 15492833,
           15492859, 15502547, 15520301,
           15527509, 15522343, 1550784]

HOST = "127.0.0.1"
PORT = 65432
TIMEOUT = 30

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(TIMEOUT)

try:
    client.connect(serv_addr)
    for number in numbers:
        client.sendall(f"{number}".encode("ascii"))
        res = client.recv(1024).decode("ascii")
        print(f"{HOST}:{PORT} - {number} - {res}")

    client.close()

except (ConnectionRefusedError, ConnectionResetError, TimeoutError, BrokenPipeError, socket.timeout):
    print("Connection problem. terminating the program.")