#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
#    this is an UART-LoRa device and thers is an firmware on Module
#    users can transfer or receive the data directly by UART and dont
#    need to set parameters like coderate,spread factor,etc.
#    |============================================ |
#    |   It does not suport LoRaWAN protocol !!!   |
#    | ============================================|
#
#    This script is mainly for Raspberry Pi 3B+, 4B, and Zero series
#    Since PC/Laptop does not have GPIO to control HAT, it should be configured by
#    GUI and while setting the jumpers,
#    Please refer to another script pc_main.py
#

import sys
import LoRa_socket
import time
import util as u

# Call with test_receiver {addr}
def run_test(arguments):
    arg_addr = int(arguments[1])
    node = LoRa_socket.LoRa_socket(addr=arg_addr)
    try:
        print("attempting to establish connection, listening for nearby nodes")
        addr = node.accept()
        if addr is None:
            raise Exception("Unable to establish connection with node")
        print(f'Connected to Node {addr}')
        while True:
            received_message = node.recv(5)
            if received_message is not None:
                (payload, addr) = received_message
                print(f'Received Message: {payload.decode()}')
            else:
                print("Did not receive a message")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_test(sys.argv)