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

# Call with test_bidirectional {true/false for tx/recv} {addr} {if tx recv_addr}
def run_test(arguments):
    arg_tx = bool(arguments[1])
    arg_addr = int(arguments[2])
    arg_recv_addr = -1
    if arg_tx:
        arg_recv_addr = int(arguments[3])
        
    print(f'Starting Test: tx:{arg_tx} self_addr:{arg_addr} recv_addr:{arg_recv_addr}')
        
    node = LoRa_socket.LoRa_socket(addr=arg_addr)
    try:
        time.sleep(1)
        if arg_tx:
            print("attempting to establish connection, broadcasting to nearby nodes")
            node.connect()
            print("Connection established. Moving on to sending:")
            while True:
                node.send(f'Temp is {u.get_cpu_temp()} deg C'.encode(), arg_recv_addr)
                received_message = node.recv(5)
                if received_message is not None:
                    print(f'Received Message: {received_message[0]}')
                else:
                    print("Did not receive a response")
                time.sleep(2)
                
        else:
            print("attempting to establish connection, listening for nearby nodes")
            node.accept()
            while True:
                received_message = node.recv(10)
                if received_message is not None:
                    (payload, addr) = received_message
                    print(f'Received Message: {payload.decode()}')
                    node.send(f'RETURN TO SENDER-${payload.decode()}'.encode(), addr)
                else:
                    print("Did not receive a message")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    run_test(sys.argv)