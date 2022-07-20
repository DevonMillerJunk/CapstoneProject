from random import random
from bitarray import bitarray
import binascii

DEFAULT_KEY: bytes = b'\xf8\xc9\x14\x0a'


class CRC:
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
                input = bitarray(curr_pick).setall(0)
            tmp ^= input
            if curr_pick < len(bits):
                tmp.append(bits[curr_pick])
            curr_pick += 1
        test = random.uniform(0,1)
        if (test < 0.33):
            tmp[self.key_len] ^= 1
        return tmp[:self.key_len].tobytes()

    def encode(self, message: str) -> bytes:
        encodedMessage = message.encode()
        bits = bitarray()
        bits.frombytes(encodedMessage)
        return encodedMessage + self.__gen_crc__(bits)

    def decode(self, message: bytes) -> str:
        bits = bitarray()
        bits.frombytes(message)
        recv_message = bits[0:len(bits) - self.key_len]
        recv_crc = bits[len(bits) - self.key_len:len(bits)].tobytes()
        if (recv_crc == self.__gen_crc__(recv_message)):
            return recv_message.tobytes().decode()
        raise Exception("Invalid message received")


# crc = CRC()
# input_message: str = "TestSendingARandomMessageToEnsureTheCrcIsWorking"
# print("Successful?: " +
#       str(crc.decode(crc.encode(input_message)) == input_message))
