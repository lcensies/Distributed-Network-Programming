import signal
import sys
import zmq


if len(sys.argv) > 2:
    serv_cli_input_port, serv_cli_output_port = int(sys.argv[1]), int(sys.argv[2])
else:
    serv_cli_input_port, serv_cli_output_port = 5555, 5556

context = zmq.Context()
# sub_sock = context.socket(zmq.SUB)
# sub_sock.connect(f"tcp://127.0.0.1:{serv_user_input_port}")
# sub_sock.setsockopt_string(zmq.SUBSCRIBE, '')
# set a timeout for receive, make it non-blocking

serv_addr = "127.0.0.1"
cli_input_req = context.socket(zmq.REQ)
cli_input_req.connect(f"tcp://{serv_addr}:{serv_cli_input_port}")

cli_output_sub = context.socket(zmq.SUB)
cli_output_sub.connect(f"tcp://{serv_addr}:{serv_cli_output_port}")
cli_output_sub.setsockopt_string(zmq.SUBSCRIBE, '')
cli_output_sub.RCVTIMEO = 100

def handle_stop_signals(signum, frame):
    print("Terminating the program.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

print("Type your message:")


while True:
    line = input("> ")
    if len(line) != 0:
        # send request to client_inputs
        # receive confirmation
        cli_input_req.send_string(line)
        msg = cli_input_req.recv_string()
        # print(msg)
    try:
        while True:
            # try to receive from client_outputs
            # print if got anything
            msg = cli_output_sub.recv_string()
            print(msg)
    except zmq.Again:
        continue
