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

#    The following is to obtain the temprature of the RPi CPU
def get_cpu_temp():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000

node = LoRa_socket.LoRa_socket()

def send_deal():
    get_rec = ""
    print("")
    print("input a string such as \033[1;32m0,915,Hello World\033[0m,it will send `Hello World` to lora node device of address 0 with 915M ")
    print("please input and press Enter key:", end='', flush=True)

    while True:
        rec = sys.stdin.read(1)
        if rec != None:
            if rec == '\x0a': break
            get_rec += rec
            sys.stdout.write(rec)
            sys.stdout.flush()

    get_t = get_rec.split(",")
    # the data format is as follows
    # "node address,frequency,payload"
    #  e.g. "20,868,Hello World"
    address = int(get_t[0])
    offset_frequency = int(get_t[1]) - (850 if int(get_t[1]) > 850 else 410)
    payload = get_t[2]

    node.send_msg(address, offset_frequency, payload)
    print('\x1b[2A', end='\r')
    print(" " * 200)
    print(" " * 200)
    print(" " * 200)
    print('\x1b[3A', end='\r')


def send_cpu_continue(continue_or_not=True):
    if continue_or_not:
        global timer_task
        global seconds
        #
        # broadcast the cpu temperature at 915MHz
        #
        offset_freq = 915 - 850
        data = "CPU Temperature:" + str(get_cpu_temp()) + " C"
        node.broadcast(data)
        time.sleep(0.2)
        timer_task = Timer(seconds, send_cpu_continue)
        timer_task.start()
    else:
        offset_freq = 915 - 850
        data = "CPU Temperature:" + str(get_cpu_temp()) + " C"
        node.broadcast(data)
        time.sleep(0.2)
        timer_task.cancel()
        pass

try:
    time.sleep(1)
    print("Press \033[1;32mEsc\033[0m to exit")
    print("Press \033[1;32mi\033[0m   to send")
    print("Press \033[1;32ms\033[0m   to send cpu temperature every 10 seconds")

    # it will send rpi cpu temperature every 10 seconds
    seconds = 10

    while True:

        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            c = sys.stdin.read(1)
            # dectect key Esc
            if c == '\x1b': break
            # dectect key i
            if c == '\x69':
                send_deal()
            # dectect key s
            if c == '\x73':
                print("Press \033[1;32mc\033[0m   to exit the send task")
                timer_task = Timer(seconds, send_cpu_continue)
                timer_task.start()

                while True:
                    if sys.stdin.read(1) == '\x63':
                        timer_task.cancel()
                        print('\x1b[1A', end='\r')
                        print(" " * 100)
                        print('\x1b[1A', end='\r')
                        break

            sys.stdout.flush()

        node.recv()
        # timer,send messages automatically

except:
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