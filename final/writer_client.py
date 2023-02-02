import signal
import sys
import zmq


if len(sys.argv) > 2:
    serv_cli_input_port, cli_name = int(sys.argv[1]), sys.argv[2]
else:
    serv_cli_input_port, cli_name = 5002, "alice"


print(f"Serv cli input port: {serv_cli_input_port}, cli_name: {cli_name}")

context = zmq.Context()

serv_addr = "127.0.0.1"
cli_input_req = context.socket(zmq.REQ)
cli_input_req.connect(f"tcp://{serv_addr}:{serv_cli_input_port}")

# cli_output_sub = context.socket(zmq.SUB)
# cli_output_sub.connect(f"tcp://{serv_addr}:{serv_cli_output_port}")
# cli_output_sub.setsockopt_string(zmq.SUBSCRIBE, '')
# cli_output_sub.RCVTIMEO = 100

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
        request = f"{cli_name}:{line}"
        cli_input_req.send_string(request)
        # print(msg)
        msg = cli_input_req.recv_string()
