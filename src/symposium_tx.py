#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import LoRa_socket
import time
import util as u
import constants as c
import traceback

# Call with test_transmitter {addr}
def run_test(arguments):
    arg_addr = int(arguments[1])
    node = LoRa_socket.LoRa_socket(addr=arg_addr, rssi=False)
    try:
        print("attempting to establish connection, broadcasting to nearby nodes")
        conn_addr = node.connect()
        if conn_addr is None:
            raise Exception("Unable to establish connection. Closing program")
            
        print(f'Connection established to node {conn_addr}')
        while True:
            input1 = input()
            len_suffix = 0 if (input1 % c.PACKET_DATA_SZ == 0) else (c.PACKET_DATA_SZ - (input1 % c.PACKET_DATA_SZ == 0))
            total_msg = (input1 + (' ' * len_suffix)).encode()
            total_bits = 8 * len(total_msg)
            start_t = time.time()
            node.send(total_msg, conn_addr)
            end_t = time.time()
            print(f'DAT:{float(total_bits) / (end_t - start_t)},{float(8 * node.sent_bytes) / (end_t - start_t)},{100 * float(node.dropped_packets) / float(node.dropped_packets + node.sent_packets + node.received_packets)}')
    except Exception as e:
        print(f'Exception in transmitter: {str(e)}')
        print(traceback.format_exc())
        print(sys.exc_info()[2])
if __name__ == "__main__":
    run_test(sys.argv)