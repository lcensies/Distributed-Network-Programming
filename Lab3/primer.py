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
serv_w_input_sub.setsockopt_string(zmq.SUBSCRIBE, 'isprime')
serv_w_input_sub.RCVTIMEO = 100
# set a timeout for receive, make it non-blocking

w_output_pub = context.socket(zmq.PUB)
w_output_pub.bind(f"tcp://{worker_addr}:{w_output_port}")

def handle_stop_signals(signum, frame):
    print("Terminating the program.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

def is_prime(n):
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for divisor in range(3, n, 2):
        if n % divisor == 0:
            return False
    return True

print(f"Primer is started")

while True:
    try:
        msg = serv_w_input_sub.recv_string()

        pattern = re.compile("^(isprime \-?[0-9]{1,19})$")

        if not pattern.match(msg):
            continue

        num = int(msg.split()[1])
        ans = is_prime(num)
        if ans:
            ret = f"{num} is prime"
        else:
            ret = f"{num} is not prime"
        print(ret)
        w_output_pub.send_string(ret)
    except zmq.Again:
        continue
