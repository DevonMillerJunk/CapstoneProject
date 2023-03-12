#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import LoRa_socket
import time
import util as u
import traceback

# Call with test_receiver {addr}
def run_test(arguments):
    arg_addr = int(arguments[1])
    node = LoRa_socket.LoRa_socket(addr=arg_addr, rssi=False)
    try:
        print("attempting to establish connection, listening for nearby nodes")
        addr = node.accept()
        if addr is None:
            raise Exception("Unable to establish connection with node")
        print(f'Connected to Node {addr}')
        real_start_t = time.time()
        while True:
            start_t = time.time()
            recv_bits: int = 0
            while time.time() - start_t < 8.0:
                received_message = node.recv(5)
                if received_message is not None:
                    (payload, addr) = received_message
                    recv_bits += 8 * len(payload.decode())
                    print(f'MSG:{payload.decode().strip()}')
                # else:
                #     print("Did not receive a message")
            end_t = time.time()
            print(f'DAT:{float(recv_bits) / (end_t - start_t)},{float(8 * node.received_bytes) / (end_t - real_start_t)},{100 * float(node.dropped_packets)/ float(node.dropped_packets + node.sent_packets + node.received_packets)}')
    except Exception as e:
        print(f'Exception in receiver: {str(e)}')
        print(traceback.format_exc())
        print(sys.exc_info()[2])

if __name__ == "__main__":
    run_test(sys.argv)