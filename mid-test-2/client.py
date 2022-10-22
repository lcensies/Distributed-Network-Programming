#!/usr/bin/python3
import random
import socket
import sys
from contextlib import closing
from time import sleep

if len(sys.argv) > 2:
    serv_addr = sys.argv[1].split(":")
    serv_addr = (serv_addr[0], int(serv_addr[1]))
    cli_name = sys.argv[2]
else:
    serv_addr = ("localhost", 5555)
    cli_name = f"User {random.randint(0, 100)}"

TIMEOUT = 30

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(TIMEOUT)

try:
    client.connect(serv_addr)
    while True:
        client.sendall(f"{cli_name}".encode("ascii"))
        sessions = client.recv(1024).decode("ascii")
        print(sessions)
        sleep(1)
except Exception as e:
    print("Terminating the client")