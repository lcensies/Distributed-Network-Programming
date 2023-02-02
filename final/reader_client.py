import signal
import sys
import zmq


if len(sys.argv) > 1:
    serv_cli_output_port = int(sys.argv[1])
else:
    serv_cli_output_port = 5001

context = zmq.Context()

serv_addr = "127.0.0.1"

cli_output_sub = context.socket(zmq.SUB)
cli_output_sub.connect(f"tcp://{serv_addr}:{serv_cli_output_port}")
cli_output_sub.setsockopt_string(zmq.SUBSCRIBE, '')
cli_output_sub.RCVTIMEO = 100

def handle_stop_signals(signum, frame):
    print("Terminating the program.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

print("Reader client started")

while True:
    try:
        while True:
            msg = cli_output_sub.recv_string()
            print(msg)
    except zmq.Again:
        continue
