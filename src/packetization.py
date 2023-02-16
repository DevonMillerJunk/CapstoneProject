from bitarray import bitarray
from bitarray.util import ba2int, int2ba
from settings import BUF_SZ
import error_encoding.crc as crc

class Packet:
    # Class variables
    
    CRC = crc.CRC()
    USE_CRC = True # Temporary while we test with/without crc
    INT_LEN = 32 # used for decoding, in bits
    # Total Packet size = payload + packet num + crc
    PACKET_DATA_SZ = BUF_SZ - INT_LEN - (USE_CRC if CRC.CRC_SZ else 0)
    
    def __init__(self, packet_num: int, payload: bytes, fragment_num: int=1, total_fragments: int=1):
        self.packet_num: int = packet_num
        self.payload: bytes  = payload
        self.fragment_num: int = fragment_num
        self.total_fragments: int = total_fragments
        
    # Creates bytes following: packet num | fragment_num | total_fragments | payload
    def __combined_packet(self) -> bytes:
        payload_bits:bitarray = bitarray()
        payload_bits.frombytes(self.payload)
        packet_num_bits:bitarray = int2ba(self.packet_num)
        fragment_num_bits: bitarray = int2ba(self.fragment_num)
        total_frag_bits: bitarray = int2ba(self.total_fragments)
        padded_0s_packet_num:bitarray = bitarray(self.INT_LEN - len(packet_num_bits))
        padded_0s_packet_num.setall(0)
        padded_0s_fragment_num:bitarray = bitarray(self.INT_LEN - len(fragment_num_bits))
        padded_0s_fragment_num.setall(0)
        padded_0s_total_frag:bitarray = bitarray(self.INT_LEN - len(total_frag_bits))
        padded_0s_total_frag.setall(0)
        return (padded_0s_packet_num + packet_num_bits +\
                padded_0s_fragment_num + fragment_num_bits +\
                padded_0s_total_frag + total_frag_bits +\
                payload_bits).tobytes()
 
    # Return the packet encoded as bytes
    def encode(self) -> bytes:
        combined_packet:bytes = self.__combined_packet()
        if self.USE_CRC:
            return self.CRC.encode(combined_packet)
        return combined_packet
 
    # Decode a given byte array into a packet
    @staticmethod
    def decode(data: bytes) -> 'Packet': # note 'Packet' is due to a weird python restriction
        result_bytes = data
        if Packet.USE_CRC:
            result_bytes = Packet.CRC.decode(data)
        bits:bitarray = bitarray()
        bits.frombytes(result_bytes)
        packet_num:int = ba2int(bits[0:Packet.INT_LEN])
        fragment_num:int = ba2int(bits[Packet.INT_LEN:2*Packet.INT_LEN])
        total_fragments:int = ba2int(bits[2*Packet.INT_LEN:3*Packet.INT_LEN])
        payload = bits[3*Packet.INT_LEN:len(bits)].tobytes()
        return Packet(packet_num, payload, fragment_num, total_fragments)
    
# input_message: str = "aosjbndoasiidboasibdoaibsdoibasoidasbljkadsnblkasnlkadsnlkas"
# encoded_input:bytes = input_message.encode()
# packet_num:int = 12089

# packet = Packet(packet_num, encoded_input)
# encoded_packet:bytes = packet.encode()
# decoded_packet = Packet.decode(encoded_packet)

# print(packet_num == decoded_packet.packet_num)
# print(input_message == decoded_packet.payload.decode())