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
import traceback

# Call with test_transmitter {addr} {test_time} (in sec)
def run_test(arguments):
    arg_addr = int(arguments[1])
    test_duration = float(arguments[2])
    node = LoRa_socket.LoRa_socket(addr=arg_addr)
    try:
        print("attempting to establish connection, broadcasting to nearby nodes")
        conn_addr = node.connect()
        if conn_addr is None:
            raise Exception("Unable to establish connection. Closing program")
            
        print(f'Connection established to node {conn_addr}')
        message = u.gen_packet().encode()
        message_len_bits = len(message) * 8
        bits_sent: int = 0 
        start_t = time.time()
        while time.time() - start_t < test_duration:
            node.send(message, conn_addr)
            bits_sent += message_len_bits
        end_t = time.time()
            
        print(f'Effective Data Rate: Sent {bits_sent} bits in {end_t - start_t} seconds. {float(bits_sent) / (end_t - start_t)}bps')
        print(f'True Data Rate: Sent {8 * node.sent_bytes} bits in {end_t - start_t} seconds. {float(8 * node.sent_bytes) / (end_t - start_t)}bps')
        print(f'Dropped Packets: {node.dropped_packets}, {100 * float(node.dropped_packets)/ float(node.sent_packets + node.received_packets)}%')
    except Exception as e:
        print(f'Exception in transmitter: {str(e)}')
        print(traceback.format_exc())
        print(sys.exc_info()[2])
if __name__ == "__main__":
    run_test(sys.argv)