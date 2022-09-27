import signal
import socket
import sys
from threading import Thread

import zmq

if len(sys.argv) > 4:
    cli_input_port, cli_output_port, w_input_port, w_output_port = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
else:
    cli_input_port, cli_output_port, w_input_port, w_output_port = 5555, 5556, 5557, 5558


serv_ip = "127.0.0.1"
worker_addr = "127.0.0.1"

cli_input_addr = f"{serv_ip}:{cli_input_port}"
cli_output_addr = f"{serv_ip}:{cli_output_port}"
w_input_addr = f"{worker_addr}:{w_input_port}"
w_output_addr = f"{worker_addr}:{w_output_port}"

context = zmq.Context()

cli_input_rep = context.socket(zmq.REP)
cli_input_rep.bind(f"tcp://{cli_input_addr}")
cli_input_rep.RCVTIMEO = 100

w_input_pub = context.socket(zmq.PUB)
w_input_pub.bind(f"tcp://{w_input_addr}")

w_output_sub = context.socket(zmq.SUB)
w_output_sub.connect(f"tcp://{w_output_addr}")
w_output_sub.setsockopt_string(zmq.SUBSCRIBE, '')
w_output_sub.RCVTIMEO = 100

cli_output_pub = context.socket(zmq.PUB)
cli_output_pub.bind(f"tcp://{cli_output_addr}")

# cli_input_sub = context.socket(zmq.SUB)
# # we bind the socket, as a server
# cli_input_sub.bind(f"tcp://{serv_addr}")
# cli_input_sub.setsockopt_string(zmq.SUBSCRIBE, '')


print(f"Server is looking for user input on {cli_input_addr}")


def start_input_handler():
    # global run_threads
    print(f"Input handler is looking for pending requests.")
    while True:
        try:
            msg = cli_input_rep.recv_string()
            if msg:
                # Reply to client that his message was received
                cli_input_rep.send_string(msg)
                cli_output_pub.send_string(msg)
                w_input_pub.send_string(msg)
            # Send message to clients output queue
        except zmq.Again:
            pass
    # while run_threads:
    # while True:
    #     try:
    #         client = q.get(block=True)
    #         # client = q.get(block=True, timeout=2)
    #         process_list(i_thread, client)
    #     except Exception as e:
    #         continue
    print(f"Stopping thread {i_thread}")


def start_result_handler():
    print(f"Work handler is looking for pending requests.")
    while True:
        try:
            msg = w_output_sub.recv_string()
            print(msg)
            cli_output_pub.send_string(msg)
            # Send message to clients output queue
        except zmq.Again:
            continue

def handle_stop_signals(signum, frame):
    print("Terminating the program.")
    sys.exit(0)

input_handler = Thread(target=start_input_handler, daemon=True)
input_handler.start()

result_handler = Thread(target=start_result_handler, daemon=True)
result_handler.start()

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

input_handler.join()


