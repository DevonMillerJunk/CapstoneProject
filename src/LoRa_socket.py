# This file is used for LoRa and Raspberry pi4B related issues

import math
import RPi.GPIO as GPIO
import serial
import time
import constants
import error_encoding.crc as crc


class LoRa_socket:

    M0 = constants.M0
    M1 = constants.M1
    # if the header is 0xC0, then the LoRa register settings dont lost when it poweroff, and 0xC2 will be lost.
    # cfg_reg = [0xC0,0x00,0x09,0x00,0x00,0x00,0x62,0x00,0x17,0x43,0x00,0x00]
    cfg_reg = [
        0xC2, 0x00, 0x09, 0x00, 0x00, 0x00, 0x62, 0x00, 0x12, 0x43, 0x00, 0x00
    ]
    get_reg = bytes(12)
    rssi = False
    addr = 65535
    serial_n = constants.SERIAL_NUM
    power = constants.POWER
    freq = constants.FREQ
    start_freq = 850
    offset_freq = constants.FREQ - start_freq
    ser = None
    connected_address = 0
    connected_freq = offset_freq
    packet_num = 0

    def __init__(self,serial_num=constants.SERIAL_NUM,freq=constants.FREQ,\
                 addr=0,power=constants.POWER,rssi=False,air_speed=constants.AIR_SPEED,\
                 net_id=0,buffer_size = constants.BUF_SZ,crypt=0,\
                 relay=False,lbt=False,wor=False):
        self.rssi = rssi
        self.addr = addr
        self.packet_num = 0
        self.freq = freq
        self.serial_n = serial_num
        self.power = power
        self.crc = crc.CRC()
        # Initial the GPIO for M0 and M1 Pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)

        # The hardware UART of Pi3B+,Pi4B is /dev/ttyS0
        self.ser = serial.Serial(serial_num, 9600)
        self.ser.flushInput()
        self.set(freq, addr, power, rssi, air_speed, net_id, buffer_size,
                 crypt, relay, lbt, wor)


    def set(self,freq,addr,power,rssi,air_speed=2400,\
            net_id=0,buffer_size = 240,crypt=0,\
            relay=False,lbt=False,wor=False):
        self.send_to = addr
        self.addr = addr
        # We should pull up the M1 pin when sets the module
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)

        low_addr = addr & 0xff
        high_addr = addr >> 8 & 0xff
        net_id_temp = net_id & 0xff
        if freq > 850:
            freq_temp = freq - 850
            self.start_freq = 850
            self.offset_freq = freq_temp
        elif freq > 410:
            freq_temp = freq - 410
            self.start_freq = 410
            self.offset_freq = freq_temp

        air_speed_temp = constants.AIR_SPEED
        buffer_size_temp = constants.BUF_SZ
        power_temp = constants.POWER

        if rssi:
            rssi_temp = 0x80
        else:
            rssi_temp = 0x00

        # get crypt
        l_crypt = crypt & 0xff
        h_crypt = crypt >> 8 & 0xff

        if relay == False:
            self.cfg_reg[3] = high_addr
            self.cfg_reg[4] = low_addr
            self.cfg_reg[5] = net_id_temp
            self.cfg_reg[
                6] = constants.SX126X_UART_BAUDRATE_9600 + air_speed_temp
            self.cfg_reg[7] = buffer_size_temp + power_temp + 0x20
            self.cfg_reg[8] = freq_temp
            self.cfg_reg[9] = 0x43 + rssi_temp
            self.cfg_reg[10] = h_crypt
            self.cfg_reg[11] = l_crypt
        else:
            self.cfg_reg[3] = 0x01
            self.cfg_reg[4] = 0x02
            self.cfg_reg[5] = 0x03
            self.cfg_reg[
                6] = constants.SX126X_UART_BAUDRATE_9600 + air_speed_temp
            self.cfg_reg[7] = buffer_size_temp + power_temp + 0x20
            self.cfg_reg[8] = freq_temp
            self.cfg_reg[9] = 0x03 + rssi_temp
            self.cfg_reg[10] = h_crypt
            self.cfg_reg[11] = l_crypt
        self.ser.flushInput()

        for i in range(2):
            self.ser.write(bytes(self.cfg_reg))
            r_buff = 0
            time.sleep(0.2)
            if self.ser.inWaiting() > 0:
                time.sleep(0.1)
                r_buff = self.ser.read(self.ser.inWaiting())
                if r_buff[0] == 0xC1:
                    print("parameters setting is :", end='')
                    for i in self.cfg_reg:
                        print(hex(i), end=' ')
                    print('\r\n')

                    print("parameters return is  :", end='')
                    for i in r_buff:
                        print(hex(i), end=' ')
                    print('\r\n')
                else:
                    print("parameters setting fail :", r_buff)
                break
            else:
                print("setting fail,setting again")
                self.ser.flushInput()
                time.sleep(0.2)
                print('\x1b[1A', end='\r')
                if i == 1:
                    print("setting fail,Press Esc to Exit and run again")
                    # time.sleep(2)
                    # print('\x1b[1A',end='\r')

        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.LOW)
        time.sleep(0.1)

    def get_settings(self):
        # the pin M1 of lora HAT must be high when enter setting mode and get parameters
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)

        # send command to get setting parameters
        self.ser.write(bytes([0xC1, 0x00, 0x09]))
        if self.ser.inWaiting() > 0:
            time.sleep(0.1)
            self.get_reg = self.ser.read(self.ser.inWaiting())

        # check the return characters from hat and print the setting parameters
        if self.get_reg[0] == 0xC1 and self.get_reg[2] == 0x09:
            fre_temp = self.get_reg[8]
            addr_temp = self.get_reg[3] + self.get_reg[4]
            air_speed_temp = self.get_reg[6] & 0x03
            power_temp = self.get_reg[7] & 0x03

            print("Frequency is {0}.125MHz.", fre_temp)
            print("Node address is {0}.", addr_temp)
            print("Air speed is {0} bps" +
                  constants.LORA_AIR_SPEED_DIC.get(None, air_speed_temp))
            print("Power is {0} dBm" +
                  constants.LORA_POWER_DIC.get(None, power_temp))
            GPIO.output(self.M1, GPIO.LOW)

    def __format_addr__(self, address: int) -> bytes:
        return bytes([address >> 8]) + bytes([address & 0xff])

    def __encode_data__(self, payload: str) -> bytes:
        encoding: bytes = self.crc.encode(payload)
        length = len(encoding)
        return bytes([length]) + encoding

    # the sending message format
    #
    # receiving node         receiving node       receiving node      own high 8bit     own low 8bit         own           message
    # high 8bit address      low 8bit address       frequency           address           address          frequency       payload
    def __send_packet(self, address: int, rec_freq: int, payload):
        data: bytes = self.__format_addr__(address) +\
            bytes([self.offset_freq]) +\
            self.__format_addr__(self.addr) +\
            bytes([self.offset_freq]) +\
            self.__encode_data__(payload)
        self.__raw_send(data)

    def send(self, address: int, rec_freq: int, payload):
        retries = 0
        response = None
        while response is None and retries <= 10:
            print("start")
            self.__send_packet(address, rec_freq, payload)
            response = self.__receive()
            if not response:
                retries += 1
        if response is not None:
            self.packet_num = int(response)
        else:
            print("packet delivery failed for " + self.packet_num)

    def broadcast(self, payload):
        data: bytes = bytes([255]) +\
                      bytes([255]) +\
                      bytes([self.offset_freq]) +\
                      bytes([255]) +\
                      bytes([255]) +\
                      bytes([self.offset_freq]) +\
                      self.__encode_data__(payload)
        self.__raw_send(data)

    def __raw_send(self, data):
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)

        self.ser.write(data)
        # if self.rssi == True:
        # self.__get_channel_rssi()
        time.sleep(0.1)

    def __send_ack(self):
        self.packet_num += 1
        data: bytes = self.__gen_header__(self.connected_address)
        data: bytes = bytes([self.connected_address >> 8]) +\
               bytes([self.connected_address & 0xff]) +\
               bytes([self.connected_freq]) +\
               bytes([self.addr >> 8]) +\
               bytes([self.addr & 0xff]) +\
               bytes([self.offset_freq]) +\
               self.__encode_data__(str(self.packet_num))
        self.__raw_send(data)

    def __receive(self, timeout: float = 1):
        curr_time: float = 0
        while self.ser.inWaiting() <= 0 and curr_time < timeout:
            time.sleep(0.1)
            curr_time += 0.1
            print("waiting")
        if self.ser.inWaiting() > 0:
            time.sleep(0.5)
            r_buff = self.ser.read(self.ser.inWaiting())
            address = (r_buff[0] << 8) + r_buff[1]
            freq = r_buff[2] + self.start_freq
            len = r_buff[3]
            msg = r_buff[4:math.min(len(r_buff), len)]
            decoded_msg = self.crc.decode(bytes(msg))

            print(
                "receive message from node address with frequency\033[1;32m %d,%d.125MHz\033[0m"
                % (address, freq),
                end='\r\n',
                flush=True)
            print("message is " + decoded_msg, end='\r\n')

            # print the rssi
            if self.rssi:
                # print('\x1b[3A',end='\r')
                print("the packet rssi value: -{0}dBm".format(256 -
                                                              r_buff[-1:][0]))
                self.__get_channel_rssi()
            else:
                pass
                #print('\x1b[2A',end='\r')
            return msg
        else:
            return None

    def recv(self):
        res = self.__receive()
        self.__send_ack()
        return res

    def connect(self):
        retries = 0
        response = None
        while response is None and retries <= 10:
            payload: str = self.addr + "," + self.offset_freq
            self.broadcast(payload)
            response = self.__receive()
            if not response:
                retries += 1
        if response is not None:
            self.connected_address = response[0]
            self.connected_freq = response[1]
            print("connected to" + self.connected_address + ", " +
                  self.connected_freq)
        else:
            print("connection attempt failed")

    def accept(self):
        listen = self.__receive()
        resp = listen.split(",")
        self.connected_address = resp[0]
        self.connected_freq = resp[1]
        payload: str = self.addr + "," + self.offset_freq
        self.__send_packet(self.connected_address, self.connected_freq,
                           payload)
        print("accepted connection request from" + self.connected_address +
              ", " + self.connected_freq)

    def __get_channel_rssi(self):
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.write(bytes([0xC0, 0xC1, 0xC2, 0xC3, 0x00, 0x02]))
        time.sleep(0.5)
        re_temp = bytes(5)
        if self.ser.inWaiting() > 0:
            time.sleep(0.1)
            re_temp = self.ser.read(self.ser.inWaiting())
        if re_temp[0] == 0xC1 and re_temp[1] == 0x00 and re_temp[2] == 0x02:
            print("the current noise rssi value: -{0}dBm".format(256 -
                                                                 re_temp[3]))
            # print("the last receive packet rssi value: -{0}dBm".format(256-re_temp[4]))
        else:
            # pass
            print("receive rssi value fail")
            # print("receive rssi value fail: ",re_temp)
