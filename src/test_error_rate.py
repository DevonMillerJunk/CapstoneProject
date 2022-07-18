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
import threading
import time
import select
import termios
import tty
from threading import Timer
import util as u

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

RX_addr = 0
TX_addr = 64

TX = True

sampleString = "CR8Jyb5hXCzXHKJV0N2e"

node_address = TX_addr
if TX == False:
    node_address = RX_addr
node = LoRa_socket.LoRa_socket(addr=node_address)


def sendString():
    node.send(RX_addr, 0, sampleString)
    time.sleep(5)


period = 5
try:
    time.sleep(1)
    print("Press \033[1;32mEsc\033[0m to exit")

    if TX:
        print("Sending Sample string every 10 seconds")
        while True:
            node.send(RX_addr, 0, sampleString)
            time.sleep(period)
    else:
        messages_received = 0
        incorrect_messages_received = 0
        bits_received = 0
        incorrect_bits_received = 0

        print("Listening for Messages:")
        while True:
            message = node.recv(2 * period)
            if (message != None):
                messages_received += 1
                (curr_BER, bits_recv,
                 correct_bits_recv) = u.BER(sampleString.encode(),
                                            message.encode())
                if (bits_recv == correct_bits_recv):
                    incorrect_messages_received += 1
                bits_received += bits_recv
                incorrect_bits_received += correct_bits_recv

                print(
                    "Received Message with BER: " + str(curr_BER) +
                    " Overall BER: " +
                    str(float(incorrect_bits_received) /
                        float(bits_received)) + " Overall FER: " + str(
                            float(incorrect_messages_received) /
                            float(messages_received)))
            else:
                print("Received None")

except Exception as e:
    print(e)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
