import socketserver
import threading

class MyUDPRequestHandler(socketserver.DatagramRequestHandler):

    def handle(self):
        print("Recieved one request from {}".format(self.client_address))

        datagram = self.rfile.readline().strip()

        print("Datagram Recieved from client is:".format(datagram))

        print(datagram)

        print("Thread Name:{}".format(threading.current_thread().name))

        self.wfile.write("Message from Server! Hello Client".encode())

server_address = ("127.0.0.1", 3434)

server = socketserver.ThreadingUDPServer(server_address, MyUDPRequestHandler)
print(f"Server is listening on {server_address}")
server.serve_forever()
