# This file is used for LoRa and Raspberry pi4B related issues

from typing import Tuple
import RPi.GPIO as GPIO
import serial
import time
import constants
import settings as s
import math
from packetization import Packet, Frame
from bitarray import bitarray
from bitarray.util import ba2int, int2ba


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
    max_retries = 10

    def __init__(self,serial_num=constants.SERIAL_NUM,freq=constants.FREQ,\
                 addr=0,power=constants.POWER,rssi=s.RSSI,air_speed=constants.AIR_SPEED,\
                 net_id=0,buffer_size = constants.BUF_SZ,crypt=0,\
                 relay=False,lbt=False,wor=False):
        self.rssi = rssi
        self.addr = addr
        self.freq = freq
        self.serial_n = serial_num
        self.power = power
        print(f'Power: {self.power} Air Speed: {air_speed} Buffer Size: {buffer_size}')
        # Initial the GPIO for M0 and M1 Pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)

        # The hardware UART of Pi3B+,Pi4B is /dev/ttyS0
        self.ser = serial.Serial(port=serial_num, baudrate=9600, timeout=1)
        self.ser.flushInput()
        self.set(freq, addr, power, rssi, air_speed, net_id, buffer_size,
                 crypt, relay, lbt, wor)
        
        # Statistics:
        self.sent_packets = 0
        self.sent_bytes = 0
        self.received_packets = 0
        self.received_bytes = 0
        self.dropped_packets = 0
        self.packet_rssis = []
        self.channel_rssi = None

    def set(self,freq,addr,power,rssi,air_speed,\
            net_id=0,buffer_size=constants.BUF_SZ,crypt=0,\
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

        if rssi:
            rssi_temp = 0x80
        else:
            rssi_temp = 0x00

        # get crypt
        l_crypt = crypt & 0xff
        h_crypt = crypt >> 8 & 0xff
        
        rssi_val = 0x20 if self.rssi else 0x00

        if relay == False:
            self.cfg_reg[3] = high_addr
            self.cfg_reg[4] = low_addr
            self.cfg_reg[5] = net_id_temp
            self.cfg_reg[6] = constants.SX126X_UART_BAUDRATE_9600 + air_speed
            self.cfg_reg[7] = buffer_size + power + rssi_val
            self.cfg_reg[8] = freq_temp
            self.cfg_reg[9] = 0x43 + rssi_temp
            self.cfg_reg[10] = h_crypt
            self.cfg_reg[11] = l_crypt
        else:
            self.cfg_reg[3] = 0x01
            self.cfg_reg[4] = 0x02
            self.cfg_reg[5] = 0x03
            self.cfg_reg[6] = constants.SX126X_UART_BAUDRATE_9600 + air_speed
            self.cfg_reg[7] = buffer_size + power + rssi_val
            self.cfg_reg[8] = freq_temp
            self.cfg_reg[9] = 0x03 + rssi_temp
            self.cfg_reg[10] = h_crypt
            self.cfg_reg[11] = l_crypt
        self.ser.flushInput()

        print(f"Registers: {self.cfg_reg}")

        for i in range(2):
            self.ser.write(bytes(self.cfg_reg))
            r_buff = 0
            time.sleep(0.2)
            if self.ser.in_waiting > 0:
                time.sleep(0.1)
                r_buff = self.ser.read(self.ser.in_waiting)
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
        if self.ser.in_waiting > 0:
            time.sleep(0.1)
            self.get_reg = self.ser.read(self.ser.in_waiting)

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
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)

    def __format_addr__(self, address: int) -> bytes:
        return bytes([address >> 8]) + bytes([address & 0xff])

    def __encode_data__(self, packet: Packet) -> bytes:
        encoding: bytes = packet.encode()
        return int2ba(len(encoding), Packet.INT_LEN).tobytes() + encoding
    
    def __raw_send(self, data: bytes):
        self.sent_packets += 1
        self.sent_bytes += len(data)
        self.ser.write(data)
        
    # the sending message format
    #
    # receiving node         receiving node       receiving node      own high 8bit     own low 8bit         own           message
    # high 8bit address      low 8bit address       frequency           address           address          frequency       payload
    def __send_packet(self, address: int, packet: Packet) -> None:
        data: bytes = self.__format_addr__(address) +\
            bytes([self.offset_freq]) +\
            self.__format_addr__(self.addr) +\
            bytes([self.offset_freq]) +\
            self.__encode_data__(packet)
        self.__raw_send(data)
        
    def __broadcast_packet(self, packet: Packet) -> None:
        data: bytes = bytes([255]) +\
            bytes([255]) +\
            bytes([self.offset_freq]) +\
            bytes([255]) +\
            bytes([255]) +\
            bytes([self.offset_freq]) +\
            self.__encode_data__(packet)
        self.__raw_send(data)

    def __send_ack(self, packet_num: int, address: int) -> None:
        self.__send_packet(address, Packet(True, packet_num, None, None))
        
    def send(self, payload: bytes, address: int) -> None:
        batch_sz = 1
        # Packetize input
        packets: list[Packet] = Frame.packetize(payload)
        
        # Send Packets
        unacked_packets = set()
        unsent_packets = set()
        for packet in packets:
            unacked_packets.add(packet.packet_num)
            unsent_packets.add(packet.packet_num)
        retries = -1
        self.clear_ser()
        while len(unacked_packets) > 0 and retries < self.max_retries:
            # Send up to batch_sz un_acked packets
            sent_packets = 0
            print("Sending packets")
            for packet in packets:
                if packet.packet_num in unacked_packets and sent_packets < batch_sz:
                    sent_packets += 1
                    self.__send_packet(address, packet)
                    unsent_packets.discard(packet.packet_num)
            
            # Remove all acks from buffer
            print("Waiting for acks")
            while len(unacked_packets) > len(unsent_packets):
                (response, addr, _, _, _) = self.__receive(4 if self.rssi else 1)
                if response is not None and response.is_ack == True and addr == address:
                    unacked_packets.discard(response.packet_num)
                else:
                    self.dropped_packets += len(unacked_packets) - len(unsent_packets)
                    break
                
            if len(unsent_packets) == 0:
                retries += 1
        if len(unacked_packets) > 0:
            print("packet delivery failed for " + str(unacked_packets))
            raise Exception("Error: Unable to transmit full payload")
     
    # Clears the serial buffer incase of packets in progress
    def clear_ser(self) -> None:
        self.ser.read(self.ser.in_waiting)
        
    # Read from SER in the safe way
    def __read_ser(self, num_bytes: int, timeout: float = 1.0) -> 'bytes | None':
        check_period: float = 0.005
        curr_time: float = 0.0
        while self.ser.in_waiting < num_bytes and curr_time < timeout:
            time.sleep(check_period)
            curr_time += check_period
            
        if self.ser.in_waiting < num_bytes:
            return None
                    
        chunk_size = 200
        read_buffer = b''
        
        # TODO: look into fixing this
        # if start_hint is not None:
        #     temp_buffer = self.ser.read_until(start_hint)
        #     # TODO: Need to check and see if it received the hint too
        #     if len(temp_buffer) is not None:
        #         read_buffer += start_hint
        
        while len(read_buffer) < num_bytes:
            # Read in chunks. Each chunk will wait as long as specified by
            # timeout. Increase chunk_size to fail quicker
            byte_chunk = self.ser.read(size=min(chunk_size, num_bytes - len(read_buffer)))
            read_buffer += byte_chunk
            if not len(byte_chunk) == chunk_size:
                break

        return read_buffer
            
        
    # Returns packet, address, freq, pkt_rssi, channel_rssi (rssi are None if self.rssi == False)
    def __receive(self, timeout: float = 1) -> Tuple['Packet | None', 'int | None', 'int | None', 'int | None', 'int | None']:
        start_t = time.time()
        retry_num = -1
        while retry_num < 10 and time.time() - start_t < timeout:
            retry_num += 1
            # Decode Header
            hdr_len = 3 + math.ceil(Packet.INT_LEN / 8)
            msg_hdr_buffer = self.__read_ser(hdr_len, timeout)
            if msg_hdr_buffer is None or len(msg_hdr_buffer) != hdr_len:
                if msg_hdr_buffer is not None:
                    self.dropped_packets += 1
                continue
            
            address = int.from_bytes(msg_hdr_buffer[0:2], "big")
            freq = msg_hdr_buffer[2]
            
            bits:bitarray = bitarray()
            bits.frombytes(msg_hdr_buffer[3:hdr_len])
            msg_len:int = ba2int(bits)
            
            if msg_len > Packet.MAX_PACKET_SZ:
                # Invalid Msg Length. Must have been an error retrieving from the serial port
                self.clear_ser()
                self.dropped_packets += 1
                continue
            
            # Decode Payload
            msg_payload_buffer = self.__read_ser(msg_len, 0.15)
            if msg_payload_buffer is None:
                self.dropped_packets += 1
                continue
            
            pkt_rssi = None
            channel_rssi = None
            
            rssi_payload = None
            if self.rssi:
                # Decode RSSI value appended to sent package
                if self.ser.in_waiting >= 1:
                    rssi_payload = self.__read_ser(1, 0.05)

                # print the rssi
                if rssi_payload is not None:
                    pkt_rssi = (256 - rssi_payload[-1:][0])*-1
                    channel_rssi = self.__get_channel_rssi()
                    self.packet_rssis.append(pkt_rssi)
                    print(f'the packet rssi value: -{pkt_rssi}dBm, channel rssi value: -{channel_rssi}dBm')
            
            try:
                packet = Packet.decode(msg_payload_buffer)
                self.received_packets += 1
                self.received_bytes += len(msg_hdr_buffer) + len(msg_payload_buffer) + (len(rssi_payload) if rssi_payload is not None else 0)
                return (packet, address, freq, pkt_rssi, channel_rssi)
            except Exception as e:
                # Try to decode another packet
                print(f'Error Occurred Decoding Packet: {e}')
        return (None, None, None, None, None)

    # Receives one frame (in bytes)
    # Returns: payload, address
    # Note: timeout is between consecutive packets, could take multiples of the timeout
    def recv(self, timeout: float = 1) -> 'Tuple[bytes, int] | None':
        (res, addr, freq, _, _) = self.__receive(timeout)
        if res is not None and addr is not None and freq is not None:
            self.connected_address = addr
            self.connected_freq = freq
            self.__send_ack(res.packet_num, addr)
            try:
                frame: Frame = Frame(res)
                while frame.all_packets_recv() == False:
                    (res, addr, _, _, _) = self.__receive(timeout)
                    if res != None and addr == self.connected_address and res.is_ack == False:
                        frame.append(res)
                        self.__send_ack(res.packet_num, addr)
                    else:
                        # Couldn't retrieve package in timeout, exiting
                        print(f'Unable to receive full package in timeout. {frame.missing_packets()} not received')
                        break
                if frame.all_packets_recv():
                    return (frame.get_payload(), self.connected_address)
            except Exception as e:
                print(f'Error Occurred Decoding Frame: {e}')
        return None

    def connect(self) -> 'int | None':
        retryPeriod = 5  #seconds
        payload: str = str(self.addr) + "," + str(self.offset_freq)
        packet = Packet(False, 0, 1, payload.encode())
        
        curr_retry = -1
        response = None
        addr = None
        freq = None
        while curr_retry <= self.max_retries:
            self.clear_ser()
            self.__broadcast_packet(packet)
            (res, addr, freq, _, _) = self.__receive(retryPeriod)
            if not res or res.is_ack == False or res.packet_num != packet.packet_num:
                curr_retry += 1
            else:
                response = res
                break
        if response is not None:
            self.connected_address = addr
            self.connected_freq = freq
            return addr
        else:
            return None

    def accept(self) -> 'int | None':
        self.clear_ser()
        listen = None
        while listen is None or listen.is_ack == True:
            (listen, _, _, _, _) = self.__receive()
        data = listen.payload.decode().split(",")
        self.connected_address = int(data[0])
        self.connected_freq = int(data[1])
        self.__send_ack(listen.packet_num, self.connected_address)
        return self.connected_address

    def __get_channel_rssi(self):
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.write(bytes([0xC0, 0xC1, 0xC2, 0xC3, 0x00, 0x02]))
        time.sleep(0.5)
        re_temp = bytes(5)
        if self.ser.in_waiting > 0:
            time.sleep(0.1)
            re_temp = self.ser.read(self.ser.in_waiting)
        if re_temp[0] == 0xC1 and re_temp[1] == 0x00 and re_temp[2] == 0x02:
            channel_rssi = (256 - re_temp[3])*-1
            print("the current noise rssi value: -{0}dBm".format(256 -
                                                                 re_temp[3]))
            # print("the last receive packet rssi value: -{0}dBm".format(256-re_temp[4]))
            self.channel_rssi = channel_rssi
            return channel_rssi
        else:
            # pass
            print("receive rssi value fail")
            # print("receive rssi value fail: ",re_temp)
            return None
