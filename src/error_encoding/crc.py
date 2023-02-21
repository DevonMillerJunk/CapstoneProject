from bitarray import bitarray
import binascii


class CRC:
    DEFAULT_KEY: bytes = b'\xf8\xc9\x14\x0a'
    CRC_SZ = len(DEFAULT_KEY) # length of CRC in bytes

    def __init__(self, key: bytes = DEFAULT_KEY, key_len=0):
        self.key = bitarray()
        self.key.frombytes(key)
        if (key_len <= 0 or key_len > len(self.key)):
            self.key_len = len(self.key)
        else:
            self.key_len = key_len

    def __bitarrayString__(self, bits: bitarray) -> str:
        return str(binascii.hexlify(bytearray(bits.tobytes())))

    def __gen_crc__(self, bits) -> bytes:
        curr_pick = self.key_len
        input = bitarray()
        tmp = self.key.copy()
        while curr_pick <= len(bits):
            if tmp[0] == 1:
                input = bits[0:curr_pick]
            else:
                input = bitarray(curr_pick)
                input.setall(0)
            tmp ^= input
            if curr_pick < len(bits):
                tmp.append(bits[curr_pick])
            curr_pick += 1
        return tmp[:self.key_len].tobytes()

    def encode(self, message: bytes) -> bytes:
        bits = bitarray()
        bits.frombytes(message)
        return message + self.__gen_crc__(bits)

    def decode(self, message: bytes) -> bytes:
        bits = bitarray()
        bits.frombytes(message)
        recv_message = bits[0:len(bits) - self.key_len]
        recv_crc = bits[len(bits) - self.key_len:len(bits)].tobytes()
        if (recv_crc == self.__gen_crc__(recv_message)):
            return recv_message.tobytes()
        raise Exception("Invalid message received")


# crc = CRC()
# input_message: str = "TestSendingARandomMessageToEnsureTheCrcIsWorking"
# encoded_input:bytes = input_message.encode()
# crc_encoded_input:bytes = crc.encode(encoded_input)
# crc_decoded_input:bytes = crc.decode(crc_encoded_input)
# decoded_input:str = str(crc_decoded_input.decode())
# successful_encoding:bool = encoded_input == crc_decoded_input
# if successful_encoding:
#     print("Successful crc encode&decode!")
# else:
#     print("Unsuccessful crc encode&decode")
