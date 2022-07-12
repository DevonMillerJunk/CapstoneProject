import math


class CRC:
    key = 0b11111000110010010001010000001010
    key_len = math.floor(math.log2(key)) + 1

    def __init__(self, crc_len):
        self.crc_len = crc_len

    def __gen_crc__(self, message):
        result = ''
        temp = '0'
        r = 0

        for i in range(len(a)):
            if int(self.key) > int(temp):
                result += '0'
                temp += message[i]
            else:
                r = temp - self.key
                if r == 0:
                    temp = message[i]
                    if (int(result) == 0):
                        result = ''
                    result += '1'
                else:
                    r = str(r).lstrip('0')
                    result += '1'
                    temp = r + message[i]
        return r

    def __encode__(self, message):
        return message + self.__gen_crc__(message)

    def __decode__(self, message):
        recv_message = message[0:len(message) - self.key_len]
        recv_crc = message[len(message) - self.key_len:len(message)]

        if (recv_crc == self.__gen_crc__(recv_message)):
            return recv_message

        raise Exception("Invalid message received")
