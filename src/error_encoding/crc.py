import math
import string

DEFAULT_KEY: string = '11111000110010010001010000001010'


class CRC:
    def __init__(self, key: string = DEFAULT_KEY, key_len=0):
        self.key = str(bin(int(key, base=2))[2:])
        if (key_len <= 0 or key_len > len(key)):
            self.key_len = len(key)
        else:
            self.key_len = key_len

    def __xor__(self, a, b):
        result = []
        for i in range(len(b)):
            if a[i] == b[i]:
                result.append('0')
            else:
                result.append('1')

        return ''.join(result)

    def __toBinary__(self, a: string):
        l, m = [], []
        for i in a:
            l.append(ord(i))
        for i in l:
            m.append(str(bin(i)[2:]))
        return ''.join(m)

    def __toBytes__(self, a: string):
        print("Input to toBytes: " + a)
        result = bytes([int(a[0:8], base=2)])
        for i in range(8, len(a), 8):
            print("Converted: " + a[i:i + 8] + " to " +
                  str(int(a[i:i + 8], base=2).to_bytes(1, 'little')))
            result += bytes([int(a[i:i + 8], base=2)])
        print("To bytes result: " + str(result))
        # 00111101111101000101100010110110
        # 3DF458B6
        return result

    def __gen_crc__(self, bytes: bytes):
        bytesString = self.__toBinary__(str(bytes))
        curr_pick = self.key_len
        input = ''
        tmp = self.key

        while curr_pick <= len(bytesString):
            if tmp[0] == '1':
                input = bytesString
            else:
                input = '0' * curr_pick
            tmp = self.__xor__(input, tmp)
            if curr_pick < self.key_len:
                tmp += bytesString[curr_pick]
            curr_pick += 1
        return self.__toBytes__(tmp)[:self.key_len]

    def encode(self, message: string):  # Message is a string, returns bytes
        return message.encode() + self.__gen_crc__(message.encode())

    def decode(self, message: bytes):  # Message is bytes, returns a string
        recv_message = message[0:len(message) - self.key_len]
        recv_crc = message[len(message) - self.key_len:len(message)]

        if (recv_crc == self.__gen_crc__(recv_message)):
            return recv_message.decode()

        raise Exception("Invalid message received")


# crc = CRC()
# input_message: string = "TestTestTestInputMessage123123123"
# print("Input message: " + input_message)
# encoded_mess = crc.encode(input_message)
# print("Encoded Message:" + str(encoded_mess))
# decoded_mess = crc.decode(encoded_mess)
# print(decoded_mess)