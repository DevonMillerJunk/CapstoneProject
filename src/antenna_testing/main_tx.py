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
import sx126x
import threading
import time
import select
import termios
import tty
import argparse
from threading import Timer

old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

#
#    Need to disable the serial login shell and have to enable serial interface
#    command `sudo raspi-config`
#    More details: see https://github.com/MithunHub/LoRa/blob/main/Basic%20Instruction.md
#
#    When the LoRaHAT is attached to RPi, the M0 and M1 jumpers of HAT should be removed.
#


#    The following is to obtain the temprature of the RPi CPU
def get_cpu_temp():
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000


#   serial_num
#       PiZero, Pi3B+, and Pi4B use "/dev/ttyS0"
#
#    Frequency is [850 to 930], or [410 to 493] MHz
#
#    address is 0 to 65535
#        under the same frequence,if set 65535,the node can receive
#        messages from another node of address is 0 to 65534 and similarly,
#        the address 0 to 65534 of node can receive messages while
#        the another note of address is 65535 sends.
#        otherwise two node must be same the address and frequence
#
#    The tramsmit power is {10, 13, 17, and 22} dBm
#
#    RSSI (receive signal strength indicator) is {True or False}
#        It will print the RSSI value when it receives each message
#

# node = sx126x.sx126x(serial_num = "/dev/ttyS0",freq=433,addr=0,power=22,rssi=False,air_speed=2400,relay=False)
node = sx126x.sx126x(serial_num="/dev/ttyS0",
                     freq=915,
                     addr=64,
                     power=22,
                     rssi=True,
                     air_speed=2400,
                     relay=False)


def send_from_stdin():
    get_rec = ""
    print("")
    print(
        "input a string such as \033[1;32m0,915,Hello World\033[0m,it will send `Hello World` to lora node device of address 0 with 915M "
    )
    print("please input and press Enter key:", end='', flush=True)

    while True:
        rec = sys.stdin.read(1)
        if rec != None:
            if rec == '\x0a': break
            get_rec += rec
            sys.stdout.write(rec)
            sys.stdout.flush()
    
    send_deal(get_rec)

def send_deal(get_rec):
  
    get_t = get_rec.split(",")

    offset_frequence = int(get_t[1]) - (850 if int(get_t[1]) > 850 else 410)
    #
    # the sending message format
    #
    #         receiving node              receiving node                   receiving node           own high 8bit           own low 8bit                 own
    #         high 8bit address           low 8bit address                    frequency                address                 address                  frequency             message payload
    data = bytes([int(get_t[0]) >> 8]) + bytes([int(get_t[0]) & 0xff]) + bytes(
        [offset_frequence]) + bytes([node.addr >> 8]) + bytes([
            node.addr & 0xff
        ]) + bytes([node.offset_freq]) + get_t[2].encode()

    node.send(data)
    # print('\x1b[2A', end='\r')
    # print(" " * 200)
    # print(" " * 200)
    # print(" " * 200)
    # print('\x1b[3A', end='\r')


def send_cpu_continue(continue_or_not=True):
    if continue_or_not:
        global timer_task
        global seconds
        #
        # broadcast the cpu temperature at 915MHz
        #

        offset_freq = 915 - 850
        data = bytes([255]) + bytes([255]) + bytes([offset_freq]) + bytes(
            [255]) + bytes([255]) + bytes(
                [node.offset_freq]) + "CPU Temperature:".encode() + str(
                    get_cpu_temp()).encode() + " C".encode()
        node.send(data)
        time.sleep(0.2)
        timer_task = Timer(seconds, send_cpu_continue)
        timer_task.start()
    else:
        data = bytes([255]) + bytes([255]) + bytes([offset_freq]) + bytes(
            [255]) + bytes([255]) + bytes(
                [node.offset_freq]) + "CPU Temperature:".encode() + str(
                    get_cpu_temp()).encode() + " C".encode()
        node.send(data)
        time.sleep(0.2)
        timer_task.cancel()
        pass

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("transmit_time", help="An int in seconds of time to be transmitting", type=int)
arg_parser.add_argument("transmit_string", help="A string to transmit", type=str)
args = arg_parser.parse_args()

try:
    time.sleep(1)
    print("Starting")
    print("Press \033[1;32mEsc\033[0m to exit")
    print("Press \033[1;32mi\033[0m to send provided string")
    # print(
    #     "Press \033[1;32ms\033[0m   to send cpu temperature every 10 seconds")

    # it will send rpi cpu temperature every 10 seconds
    seconds = 10

    while True:

        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            c = sys.stdin.read(1)

            # dectect key Esc
            if c == '\x1b': break
            # dectect key i
            if c == '\x69':
                # Send data for 15s
                t_end = time.time() + args.transmit_time
                while time.time() < t_end:      
                    send_deal(get_rec=f"0,915,{args.transmit_string}")
                print("Completed One Cycle")
            # # dectect key s
            # if c == '\x73':
            #     print("Press \033[1;32mc\033[0m   to exit the send task")
            #     timer_task = Timer(seconds, send_cpu_continue)
            #     timer_task.start()

            #     while True:
            #         if sys.stdin.read(1) == '\x63':
            #             timer_task.cancel()
            #             print('\x1b[1A', end='\r')
            #             print(" " * 100)
            #             print('\x1b[1A', end='\r')
            #             break

            sys.stdout.flush()

        #node.receive()

        # timer,send messages automatically

except Exception as e:
    print(f"Exception: {e}")
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