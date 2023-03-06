import random
from typing import List
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from settings import BUF_SZ
import error_encoding.crc as crc
import error_encoding.rsc as rsc
import math
import util as u

# A Packet is a logical grouping of data that 
# will be sent individually over the network
# To transmit, call packet.encode()
# To recv, call packet = Packet.decode()
class Packet:
    # Class variables
    CRC = crc.CRC()
    RSC = rsc.ReedSoloman()
    USE_ERR_ENC:bool = True # Temporary while we test with/without error encoding
    CRC_METHOD:bool = False # if true use CRC else use RSC
    INT_LEN:int = 16 # used for decoding, in bits
    # MAX_PACKET_SZ (bytes) should be <= BUF_SZ - 5 (header length)
    MAX_PACKET_SZ: int = BUF_SZ - 8 # Require 8 bytes for the LoRa header
    # Total Packet size (MAX_PACKET_SZ) = payload + packet_num + total_packets + crc + is_ack (in bytes)
    PACKET_DATA_SZ:int = (MAX_PACKET_SZ) - 1 - (2 * math.ceil(INT_LEN / 8)) - (0 if not USE_ERR_ENC else (CRC.CRC_SZ if CRC_METHOD else RSC.rsc_len(MAX_PACKET_SZ)))
    
    # Constructor
    # If is_ack is true, total_packets and payload are not used
    def __init__(self, is_ack: bool, packet_num: int, total_packets: int, payload: bytes):
        if packet_num < 0:
            raise Exception("Invalid Packet Num")
        self.packet_num: int = packet_num
        self.is_ack: bool = is_ack # is a data packet or an ack packet
        if is_ack == True:
            self.total_packets = None
            self.payload = None
        else:
            if packet_num >= total_packets:
                raise Exception("Invalid Packet Num")
            if len(payload) > self.PACKET_DATA_SZ:
                raise Exception("Invalid Packet Payload length")
            if total_packets < 0:
                raise Exception("Invalid Total Packets Num")
            self.total_packets: int = total_packets # number of packets for this message
            self.payload: bytes  = payload # Must be <= PACKET_DATA_SZ bytes in length.
        
    # Getters
    def get_payload(self) -> bytes:
        return self.payload
    def get_packet_num(self) -> int:
        return self.packet_num
    def get_total_packets(self) -> int:
        return self.total_packets
    
    # Byte representing is_ack
    def __is_ack_bits(self) -> bitarray:
        return bitarray('11111111') if self.is_ack else bitarray('00000000')
        
    # Creates bytes following: is_ack | packet num | total_packets | payload
    # or for an ack: is_ack | packet_num
    def __combined_packet(self) -> bytes:
        if self.is_ack:
            return (self.__is_ack_bits() + int2ba(self.packet_num, self.INT_LEN)).tobytes()
        else:
            payload_bits:bitarray = bitarray()
            payload_bits.frombytes(self.payload)
            return (self.__is_ack_bits() + int2ba(self.packet_num, self.INT_LEN) + int2ba(self.total_packets, self.INT_LEN) + payload_bits).tobytes()
 
    # Return the packet encoded as bytes
    def encode(self) -> bytes:
        combined_packet:bytes = self.__combined_packet()
        if self.USE_ERR_ENC:
            if self.CRC_METHOD:
                return self.CRC.encode(combined_packet)
            else:
                return self.RSC.encode(combined_packet)
        return combined_packet
        
    # Decode a given byte array into a packet
    # Python doesn't allow multiple constructors
    @staticmethod
    def decode(data: bytes) -> 'Packet': # note 'Packet' is due to a weird python restriction
        result_bytes = data
        if Packet.USE_ERR_ENC:
            if Packet.CRC_METHOD:
                result_bytes = Packet.CRC.decode(data)
            else:
                result_bytes = Packet.RSC.decode(data)
        bits:bitarray = bitarray()
        bits.frombytes(result_bytes)
        is_ack: bool = False if ba2int(bits[0:8]) == 0 else True
        packet_num:int = ba2int(bits[8:8+Packet.INT_LEN])
        if is_ack == True:
            return Packet(True, packet_num, None, None)
        else:
            total_packets:int = ba2int(bits[8+Packet.INT_LEN:8+2*Packet.INT_LEN])
            payload = bits[8+2*Packet.INT_LEN:len(bits)].tobytes()
            return Packet(False, packet_num, total_packets, payload)

# Represents a payload of data that will be sent in 1+ packets
# over the network. Can be used to store and decode incoming packets.
# SENDING DATA: use Frame.packetize((bytes) payload) -> List of Packets
# RECEIVING DATA:
#   1. On first packet received, frame = Frame(packet)
#   2. For every frame received, call frame.append(packet)
#   3. Detect missing frames: frame.missing_packets()
#   4. When frame.all_packets_recv() == true, can call frame.get_payload()
class Frame:
    def __init__(self, first_packet: Packet):
        # first_packet is just the first packet received,
        # doesn't need to be logically first
        if first_packet.is_ack == True:
            raise Exception("Error: cannot decode frame with ACK packet")
        self.total_packets: int = first_packet.get_total_packets()
        self.packets: List[Packet] = []
        for i in range(self.total_packets):
            if i == first_packet.get_packet_num():
                self.packets.append(first_packet)
            else:
                self.packets.append(None)
    
    # append the received packet to the frame
    # return true if the packet hasn't been received yet
    def append(self, packet: Packet) -> bool:
        ## TODO: keep these for testing, consider commenting out once code properly tested
        if packet.is_ack == True:
            raise Exception("Error: cannot decode frame with ACK packet")
        if self.packets[packet.get_packet_num()] != None:
            raise Exception("Warning: Overwritting received packet")
        if self.total_packets != packet.get_total_packets():
            raise Exception("Warning: Mismatched frame total_packets amount")
        result = True if self.packets[packet.get_packet_num()] == None else False
        self.packets[packet.get_packet_num()] = packet
        return result
      
    # determine which packets are missing  
    def missing_packets(self) -> List[int]:
        return [i for i in range(len(self.packets)) if self.packets[i] == None]
    
    # returns true if all packets have been received
    def all_packets_recv(self) -> bool:
        return all(packet != None for (packet) in self.packets)
        
    def get_payload(self) -> bytes:
        if self.all_packets_recv() == False:
            raise Exception("Warning: must have received all packets to get payload")
        result:bitarray = bitarray()
        for i in range(self.total_packets):
            packet_payload = bitarray()
            packet_payload.frombytes(self.packets[i].get_payload())
            result += packet_payload
        return result.tobytes()
    
    @staticmethod
    def packetize(payload: bytes) -> List[Packet]:
        total_packets: int = math.ceil(len(payload) / Packet.PACKET_DATA_SZ)
        payload_bits:bitarray = bitarray()
        payload_bits.frombytes(payload)
        packets:List[Packet] = []
        bit_per_packet = Packet.PACKET_DATA_SZ * 8
        for i in range(total_packets):
            packets.append(Packet(False, i, total_packets, payload_bits[i*bit_per_packet:min(len(payload_bits), (i+1)*bit_per_packet)].tobytes()))
        return packets    
   
def packet_test1():
    print("### RUNNING PACKET TEST ###")
    print("Testing Data Packet:")
    input_message: str = "aosjbndoasiidboasibdoaibsdoibasoidasbljkadsnblkasnlkadsnlkas"
    encoded_input:bytes = input_message.encode()
    packet_num:int = 12089

    packet = Packet(False, packet_num, packet_num + 1, encoded_input)
    encoded_packet:bytes = packet.encode()
    decoded_packet = Packet.decode(encoded_packet)

    print(f'Matching packet num decoded: {packet_num == decoded_packet.packet_num}')
    print(f'Matching payload decoded: {input_message == decoded_packet.payload.decode()}')
    
    print("Testing Ack Packet:")
    ack_packet = Packet(True, packet_num, None, None)
    encoded_ack_packet:bytes = ack_packet.encode()
    decoded_ack_packet = Packet.decode(encoded_ack_packet)
    print(f'Matching packet num decoded: {packet_num == decoded_ack_packet.packet_num}')
    print(f'Matching packet is ack: {decoded_ack_packet.is_ack}')
    
def frame_test1():
    print("### RUNNING FRAME TEST ###")
    input_message: str = u.genLongLoremIpsom()
    encoded_input:bytes = input_message.encode()
    
    frames_to_send = Frame.packetize(encoded_input)
    print(f'Sending {len(frames_to_send)} frames')
    
    # Shuffle the list to ensure correctness under misordered receiving
    random.shuffle(frames_to_send)
    
    recv_frame: Frame = Frame(frames_to_send[0])
    for i in range(1, len(frames_to_send)):
        recv_frame.append(frames_to_send[i])
    if len(recv_frame.missing_packets()) != 0 or recv_frame.all_packets_recv() == False:
        print("Still missing packets")
    decoded_message: str = recv_frame.get_payload().decode()
    print(f'Returned message equal? {decoded_message == input_message}')

# packet_test1()
# frame_test1()