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

# Call with test_receiver {addr}
def run_test(arguments):
    arg_addr = int(arguments[1])
    get_rssi = arguments[2].lower().capitalize() == "True"
    node = LoRa_socket.LoRa_socket(addr=arg_addr, rssi=get_rssi)
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
            while time.time() - start_t < 15.0:
                received_message = node.recv(5)
                if received_message is not None:
                    (payload, addr) = received_message
                    recv_bits += 8 * len(payload.decode())
                # else:
                #     print("Did not receive a message")
            end_t = time.time()
            print(f'Effective Received {recv_bits} bits in {end_t - start_t} seconds. {float(recv_bits) / (end_t - start_t)}bps')
            print(f'True (Includes Header Data) Data Rate: Sent {8 * node.received_bytes} bits in {end_t - real_start_t} seconds. {float(8 * node.received_bytes) / (end_t - real_start_t)}bps')
            print(f'(Lower Bound) Dropped Packets: {node.dropped_packets}, {100 * float(node.dropped_packets)/ float(node.dropped_packets + node.sent_packets + node.received_packets)}%')
    except Exception as e:
        print(f'Exception in receiver: {str(e)}')
        print(traceback.format_exc())
        print(sys.exc_info()[2])

if __name__ == "__main__":
    run_test(sys.argv)