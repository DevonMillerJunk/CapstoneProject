import random
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
    USE_CRC:bool = True # Temporary while we test with/without crc
    INT_LEN:int = 16 # used for decoding, in bits
    # Total Packet size (in bytes) = payload + packet_num + total_packets + crc + is_ack = BUF_SZ
    PACKET_DATA_SZ:int = BUF_SZ - 1 - (2 * math.ceil(INT_LEN / 8)) - (CRC.CRC_SZ if USE_CRC else 0)
    
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
    def append(self, packet: Packet):
        ## TODO: keep these for testing, consider commenting out once code properly tested
        if packet.is_ack == True:
            raise Exception("Error: cannot decode frame with ACK packet")
        if self.packets[packet.get_packet_num()] != None:
            raise Exception("Warning: Overwritting received packet")
        if self.total_packets != packet.get_total_packets():
            raise Exception("Warning: Mismatched frame total_packets amount")
        self.packets[packet.get_packet_num()] = packet
      
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
        print(f'Creating {total_packets} packets with {Packet.PACKET_DATA_SZ} bytes of data in each packet.')
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
    input_message: str = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Dignissim convallis aenean et tortor. Suspendisse sed nisi lacus sed viverra tellus. Nisl condimentum id venenatis a. Sociis natoque penatibus et magnis dis parturient. Egestas maecenas pharetra convallis posuere morbi leo urna. Pharetra et ultrices neque ornare aenean euismod elementum nisi quis. Eget felis eget nunc lobortis mattis aliquam faucibus purus in. Amet dictum sit amet justo donec enim. Consectetur libero id faucibus nisl. In metus vulputate eu scelerisque felis imperdiet proin fermentum. Orci dapibus ultrices in iaculis nunc sed augue lacus. Fusce ut placerat orci nulla pellentesque dignissim enim. Viverra accumsan in nisl nisi scelerisque eu ultrices vitae. Sed augue lacus viverra vitae congue eu consequat ac felis.
        Enim nec dui nunc mattis enim. Scelerisque mauris pellentesque pulvinar pellentesque. Adipiscing bibendum est ultricies integer quis. A diam sollicitudin tempor id eu nisl nunc mi. Purus ut faucibus pulvinar elementum integer enim neque. Mauris augue neque gravida in fermentum et sollicitudin. Aliquam nulla facilisi cras fermentum odio. Pharetra pharetra massa massa ultricies mi quis hendrerit dolor magna. In fermentum posuere urna nec tincidunt praesent semper feugiat. Aenean pharetra magna ac placerat. Aliquam vestibulum morbi blandit cursus risus at. Vitae semper quis lectus nulla at volutpat diam ut. Ultrices vitae auctor eu augue ut. Egestas purus viverra accumsan in nisl nisi scelerisque. Cursus risus at ultrices mi tempus imperdiet nulla. Mattis enim ut tellus elementum sagittis vitae.
        Erat velit scelerisque in dictum non. Dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim cras tincidunt. Adipiscing elit pellentesque habitant morbi tristique senectus et netus. Dui faucibus in ornare quam viverra orci. Enim neque volutpat ac tincidunt vitae semper quis lectus. Aliquet nec ullamcorper sit amet risus nullam eget felis. Libero nunc consequat interdum varius sit. Sit amet cursus sit amet dictum sit amet. A diam sollicitudin tempor id eu nisl nunc mi ipsum. Sed vulputate mi sit amet mauris commodo quis imperdiet massa. Mauris commodo quis imperdiet massa tincidunt nunc. In aliquam sem fringilla ut morbi tincidunt augue interdum. Nulla at volutpat diam ut. Tortor posuere ac ut consequat semper viverra nam libero. Tellus at urna condimentum mattis. Congue quisque egestas diam in.
        Cras ornare arcu dui vivamus. Sed tempus urna et pharetra pharetra. Massa sapien faucibus et molestie ac feugiat. Egestas erat imperdiet sed euismod nisi porta lorem. Mi proin sed libero enim sed faucibus. Diam maecenas sed enim ut sem viverra. Turpis massa tincidunt dui ut ornare lectus sit amet. Vitae aliquet nec ullamcorper sit amet risus nullam. Mauris cursus mattis molestie a. Curabitur vitae nunc sed velit dignissim sodales ut eu sem. Quis vel eros donec ac odio tempor orci dapibus ultrices. Neque viverra justo nec ultrices dui sapien eget mi. Urna neque viverra justo nec ultrices. Gravida rutrum quisque non tellus orci. Sem nulla pharetra diam sit amet nisl suscipit adipiscing. Nibh mauris cursus mattis molestie a.
        Mauris cursus mattis molestie a iaculis at erat pellentesque adipiscing. Odio morbi quis commodo odio aenean sed adipiscing. Ut sem viverra aliquet eget sit amet. Vel fringilla est ullamcorper eget nulla facilisi. Vitae proin sagittis nisl rhoncus. Iaculis at erat pellentesque adipiscing commodo elit at. Suscipit adipiscing bibendum est ultricies. Elit eget gravida cum sociis natoque penatibus. Quis vel eros donec ac odio. Amet est placerat in egestas erat imperdiet sed. Bibendum neque egestas congue quisque egestas diam in arcu cursus. Tortor id aliquet lectus proin nibh. In fermentum posuere urna nec. Faucibus turpis in eu mi bibendum neque egestas congue quisque. Aliquam etiam erat velit scelerisque in dictum. Facilisis leo vel fringilla est. Purus sit amet luctus venenatis lectus. Dignissim enim sit amet venenatis urna cursus eget nunc. Nascetur ridiculus mus mauris vitae ultricies leo integer malesuada."""
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