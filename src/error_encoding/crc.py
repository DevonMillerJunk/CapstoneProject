import math

DEFAULT_KEY = b'11111000110010010001010000001010'


class CRC:
    def __init__(self, key=DEFAULT_KEY, key_len=0):
        self.key = key
        if (key_len <= 0 or key_len > len(key)):
            self.key_len = len(key)
        else:
            self.key_len = key_len

    def __gen_crc__(self, bytes):
        # result = ''
        # temp = '0'
        # r = 0

        # for i in range(len(bytes)):
        #     if int(self.key) > int(temp):
        #         result += '0'
        #         temp += bytes[i]
        #     else:
        #         r = temp - self.key
        #         if r == 0:
        #             temp = bytes[i]
        #             if (int(result) == 0):
        #                 result = ''
        #             result += '1'
        #         else:
        #             r = str(r).lstrip('0')
        #             result += '1'
        #             temp = r + bytes[i]
        # return r
        return self.key[:self.key_len]

    def encode(self, message):  # Message is a string, returns bytes
        return message.encode() + self.__gen_crc__(message)

    def decode(self, message):  # Message is bytes, returns a string
        recv_message = message[0:len(message) - self.key_len]
        recv_crc = message[len(message) - self.key_len:len(message)]

        if (recv_crc == self.__gen_crc__(recv_message)):
            return recv_message.decode()

        raise Exception("Invalid message received")


# crc = CRC()
# input_message = "TestTestTestInputMessage"
# print("Input message: " + input_message)
# encoded_mess = crc.encode(input_message)
# print("Encoded Message:" + str(encoded_mess))
# decoded_mess = crc.decode(encoded_mess)
# print(decoded_mess)