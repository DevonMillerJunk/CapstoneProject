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

# Call with test_bidirectional {true/false for tx/recv} {addr}
def run_test(arguments):
    arg_tx = arguments[1].lower().capitalize() == "True"
    arg_addr = int(arguments[2])
        
    print(f'Starting Test: tx:{arg_tx} self_addr:{arg_addr}')
        
    node = LoRa_socket.LoRa_socket(addr=arg_addr)
    try:
        time.sleep(1)
        if arg_tx:
            print("attempting to establish connection, broadcasting to nearby nodes")
            conn_addr = node.connect()
            if conn_addr is not None:
                print("Connection established. Moving on to sending:")
                while True:
                    message = f'Temp is {u.get_cpu_temp()} deg C'
                    print(f'Sending: {message}')
                    node.send(message.encode(), conn_addr)
                    received_message = node.recv(5)
                    if received_message is not None:
                        print(f'Received Message: {received_message[0].decode()}')
                    else:
                        print("Did not receive a response")
                    time.sleep(2)
            else:
                print("Unable to establish connection. Closing program")
        else:
            print("attempting to establish connection, listening for nearby nodes")
            node.accept()
            while True:
                received_message = node.recv(10)
                if received_message is not None:
                    (payload, addr) = received_message
                    print(f'Received Message: {payload.decode()}')
                    return_msg = f'RETURN TO SENDER-{payload.decode()}'
                    print(f'Sending: {return_msg}')
                    node.send(return_msg.encode(), addr)
                    print(f'Delivered')
                else:
                    print("Did not receive a message")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_test(sys.argv)