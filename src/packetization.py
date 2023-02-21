from typing import List
from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from settings import BUF_SZ
import error_encoding.crc as crc
import math

# A Packet is a logical grouping of data that 
# will be sent individually over the network
# To transmit, call packet.encode()
# To recv, call packet = Packet.decode()
class Packet:
    # Class variables
    CRC = crc.CRC()
    USE_CRC = True # Temporary while we test with/without crc
    INT_LEN = 16 # used for decoding, in bits
    # Total Packet size (in bytes) = payload + packet_num + total_packets + crc = BUF_SZ
    PACKET_DATA_SZ = BUF_SZ - (2 * (INT_LEN / 8)) - (CRC.CRC_SZ if USE_CRC else 0)
    
    # Constructor
    def __init__(self, packet_num: int, total_packets: int, payload: bytes):
        if len(payload) > self.PACKET_DATA_SZ:
            raise Exception("Invalid Packet Payload length")
        if packet_num < 0 or packet_num >= total_packets:
            raise Exception("Invalid Packet Num")
        if total_packets < 0:
            raise Exception("Invalid Total Packets Num")
        self.packet_num: int = packet_num
        self.total_packets: int = total_packets # number of packets for this message
        self.payload: bytes  = payload # Must be <= PACKET_DATA_SZ bytes in length.
        
    # Getters
    def get_payload(self) -> bytes:
        return self.payload
    def get_packet_num(self) -> int:
        return self.packet_num
    def get_total_packets(self) -> int:
        return self.total_packets
        
    # Creates bytes for the packet num
    def __int_to_bits(self, num: int) -> bitarray:
        packet_num_bits:bitarray = int2ba(num)
        padded_0s:bitarray = bitarray(self.INT_LEN - len(packet_num_bits))
        padded_0s.setall(0)
        return padded_0s + packet_num_bits
        
    # Creates bytes following: packet num | total_packets | payload
    def __combined_packet(self) -> bytes:
        payload_bits:bitarray = bitarray()
        payload_bits.frombytes(self.payload)
        return (self.__int_to_bits(self.packet_num) + self.__int_to_bits(self.total_packets) + payload_bits).tobytes()
 
    # Return the packet encoded as bytes
    def encode(self) -> bytes:
        combined_packet:bytes = self.__combined_packet()
        if self.USE_CRC:
            return self.CRC.encode(combined_packet)
        return combined_packet
 
    # Decode a given byte array into a packet
    # Python doesn't allow multiple constructors
    @staticmethod
    def decode(data: bytes) -> 'Packet': # note 'Packet' is due to a weird python restriction
        result_bytes = data
        if Packet.USE_CRC:
            result_bytes = Packet.CRC.decode(data)
        bits:bitarray = bitarray()
        bits.frombytes(result_bytes)
        packet_num:int = ba2int(bits[0:Packet.INT_LEN])
        total_packets:int = ba2int(bits[Packet.INT_LEN:2*Packet.INT_LEN])
        payload = bits[2*Packet.INT_LEN:len(bits)].tobytes()
        return Packet(packet_num, total_packets, payload)

# Represents a payload of data that will be sent in 1+ packets
# over the network. Can be used to store and decode incoming packets.
# SENDING DATA: use Frame.packetize((bytes) payload) -> List of Packets
# RECEIVING DATA:
#   1. On first packet received, frame = Frame(packet)
#   2. For every frame received, call frame.append(packet)
#   3. Detect missing frames: frame.missing_packets()
#   4. When frame.all_packets_recv() == true, can call frame.get_payload()
class Frame:
    def __init__(self, first_payload: bytes):
        # first_packet is just the first packet received,
        # doesn't need to be logically first
        first_packet = Packet.decode(first_payload)
        self.total_packets: int = first_packet.get_total_packets()
        self.packets: List[Packet] = []
        for i in range(self.total_packets):
            if i == first_packet.get_packet_num():
                self.packets.append(first_packet)
            else:
                self.packets.append(None)
    
    # append the received payload to the frame
    # returns the packet number of the received packet
    def append(self, payload: bytes) -> int:
        packet = Packet.decode(payload)
        ## TODO: keep these for testing, consider commenting out once code properly tested
        if self.packets[packet.get_packet_num()] != None:
            raise Exception("Warning: Overwritting received packet")
        if self.total_packets != packet.get_total_packets():
            raise Exception("Warning: Mismatched frame total_packets amount")
        self.packets[packet.get_packet_num()] = packet
        return packet.get_packet_num()
      
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
            packet_payload.frombytes(self.packets[i].get_payload)
            result += packet_payload
        return result
    
    @staticmethod
    def packetize(payload: bytes) -> List[Packet]:
        total_packets: int = math.ceil(Packet.PACKET_DATA_SZ / len(payload))
        payload_bits:bitarray = bitarray()
        payload_bits.frombytes(payload)
        packets:List[Packet] = []
        bit_per_packet = Packet.PACKET_DATA_SZ * 8
        for i in range(total_packets):
            packets.append(Packet(i, total_packets, payload_bits[i*bit_per_packet:min(len(payload_bits, (i+1)*bit_per_packet))].tobytes()))
        return packets    
    
# input_message: str = "aosjbndoasiidboasibdoaibsdoibasoidasbljkadsnblkasnlkadsnlkas"
# encoded_input:bytes = input_message.encode()
# packet_num:int = 12089

# packet = Packet(packet_num, encoded_input)
# encoded_packet:bytes = packet.encode()
# decoded_packet = Packet.decode(encoded_packet)

# print(packet_num == decoded_packet.packet_num)
# print(input_message == decoded_packet.payload.decode())