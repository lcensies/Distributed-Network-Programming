from socket import socket, AF_INET, SOCK_STREAM

BUFF_SIZE = 1024

addr = ("127.0.0.1", 50505)

# if __name__ == "main":
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(addr)

while True:
    try:
        str_in = input("Enter string: ")
        sock.send(str_in.encode())
        result = sock.recv(BUFF_SIZE)
        print("Hash:", result.decode())
    except KeyboardInterrupt:
        sock.close()
        exit()