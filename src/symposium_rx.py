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
        while True:
            received_message = node.recv(5)
            if received_message is not None:
                (payload, _) = received_message
                print(payload.decode().strip())
            else:
                print(f'DAT:{0.0},{0},{0.0}')
    except Exception as e:
        print(f'Exception in receiver: {str(e)}')
        print(traceback.format_exc())
        print(sys.exc_info()[2])

if __name__ == "__main__":
    run_test(sys.argv)