import signal
import socket
import sys
import threading
from threading import Thread
from time import sleep
from typing import Dict
import traceback
import sys
import zmq

if len(sys.argv) > 2:
    serv_writer_port, serv_reader_port = int(sys.argv[1]), int(sys.argv[2])
else:
    serv_reader_port, serv_writer_port = 5001, 5002

# print(f"Serv cli input port: {serv_cli_input_port}, cli_name: {cli_name}")

INTERVAL_DURATION = 5

serv_reader_addr = f"127.0.0.1:{serv_reader_port}"
serv_writer_addr = f"127.0.0.1:{serv_writer_port}"

context = zmq.Context()

serv_writer_rep = context.socket(zmq.REP)
serv_writer_rep.bind(f"tcp://{serv_writer_addr}")
serv_writer_rep.RCVTIMEO = 100

serv_reader_pub = context.socket(zmq.PUB)
serv_reader_pub.bind(f"tcp://{serv_reader_addr}")

print(f"Server is listening for writers on {serv_writer_addr}")
print(f"Server is publishing for readers on {serv_reader_addr}")

storage: Dict[str, int] = {}

event = threading.Event()

def prepare_summary():
    summary = "SUMMARY:\n"
    for client in sorted(storage.keys()):
        summary += f"\t{client}: {storage[client]}\n"
        storage[client] = 0
    return summary


def start_worker():
    # global run_threads
    print(f"Input handler is looking for pending requests.")
    while True:
        try:
            if event.is_set():
                summary = prepare_summary()
                serv_reader_pub.send_string(summary)
                event.clear()
                # storage = {}
            msg = serv_writer_rep.recv_string()
            if msg:
                # Reply to writer that message has received
                serv_writer_rep.send_string(msg)
                print(msg)

                serv_reader_pub.send_string(msg)
                msg = msg.split(":")
                name, line = msg[0], msg[1]
                if not name in storage:
                    storage[name] = 0
                else:
                    storage[name] = storage[name] + 1
        # except zmq.Again:
        except Exception as e:
            # 
            if not isinstance(e, zmq.Again):
                print(traceback.format_exc())
            continue

    # print(f"Stopping thread {i_thread}")


def start_event_setter():
    global storage
    while True:
        sleep(INTERVAL_DURATION)
        event.set()
        
def handle_stop_signals(signum, frame):
    print("Terminating the program.")
    sys.exit(0)

input_handler = Thread(target=start_worker, daemon=True)
input_handler.start()

event_setter = Thread(target=start_event_setter, daemon=True)
event_setter.start()

signal.signal(signal.SIGINT, handle_stop_signals)
signal.signal(signal.SIGTERM, handle_stop_signals)

input_handler.join()