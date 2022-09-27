import signal
import socket
import sys
import re
import zmq

if len(sys.argv) > 2:
    w_input_port, w_output_port = int(sys.argv[1]), int(sys.argv[2])
else:
    w_input_port, w_output_port = 5557, 5558

serv_addr = "127.0.0.1"
worker_addr = "127.0.0.1"

context = zmq.Context()
serv_w_input_sub = context.socket(zmq.SUB)
serv_w_input_sub.connect(f"tcp://{serv_addr}:{w_input_port}")
serv_w_input_sub.setsockopt_string(zmq.SUBSCRIBE, 'gcd')
serv_w_input_sub.RCVTIMEO = 100
# set a timeout for receive, make it non-blocking

w_output_pub = context.socket(zmq.PUB)
w_output_pub.bind(f"tcp://{worker_addr}:{w_output_port}")

def handle_stop_signals(signum, frame):
    print("Terminating the program.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

def get_gcd(a, b):
    if b == 0:
        return a
    return get_gcd(b, a % b)

print(f"Gcd is started")

while True:
    try:
        msg = serv_w_input_sub.recv_string()

        pattern = re.compile("^(gcd \-?[0-9]{1,19} \-?[0-9]{1,19})$")

        if not pattern.match(msg):
            continue

        a, b = int(msg.split()[1]), int(msg.split()[2])
        ans = get_gcd(a, b)

        ret = f"gcd of {a} and {b} is {ans}"

        print(ret)
        w_output_pub.send_string(ret)
    except zmq.Again:
        continue
