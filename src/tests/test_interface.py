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

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

TX = True


#    The following is to obtain the temprature of the RPi CPU
def get_cpu_temp():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000


node_address = 64
if TX == False:
    node_address = 0
node = LoRa_socket.LoRa_socket(addr=node_address)


def send_deal():
    get_rec = ""
    print("")
    print(
        "input a string such as `Hello World` it will send `Hello World` to the connected lora node"
    )
    print("please input and press Enter key:", end='', flush=True)

    while True:
        rec = sys.stdin.read(1)
        if rec != None:
            if rec == '\x0a': break
            get_rec += rec
            sys.stdout.write(rec)
            sys.stdout.flush()

    get_t = get_rec
    # the data format is as follows
    # "node address,frequency,payload"
    #  e.g. "20,868,Hello World"
    payload = get_t

    node.send(payload)
    print('\x1b[2A', end='\r')
    print(" " * 200)
    print(" " * 200)
    print(" " * 200)
    print('\x1b[3A', end='\r')


def send_cpu_continue():
    data = "CPU Temperature:" + str(get_cpu_temp()) + " C"
    node.send(0, 915, data)
    time.sleep(0.2)


try:
    time.sleep(1)
    print("Press \033[1;32mEsc\033[0m to exit")
    print("Press \033[1;32mi\033[0m   to send")
    print(
        "Press \033[1;32ms\033[0m   to send cpu temperature every 10 seconds")

    # it will send rpi cpu temperature every 10 seconds
    seconds = 10

    if TX:
        print("attempting to establish connection, broadcasting to nearby nodes")
        node.connect()
        while True:
            send_cpu_continue()
            time.sleep(5)
    else:
        print("attempting to establish connection, listening for nearby nodes")
        node.accept()
        while True:
            node.recv(10)

except Exception as e:
    print(e)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    # print('\x1b[2A',end='\r')
    # print(" "*100)
    # print(" "*100)
    # print('\x1b[2A',end='\r')

termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
# print('\x1b[2A',end='\r')
# print(" "*100)
# print(" "*100)
# print('\x1b[2A',end='\r')
