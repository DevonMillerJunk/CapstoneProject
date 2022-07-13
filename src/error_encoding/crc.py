import math


class CRC:
    key = "11111000110010010001010000001010"

    def __gen_crc__(self, message):
        # result = ''
        # temp = '0'
        # r = 0

        # for i in range(len(message)):
        #     if int(self.key) > int(temp):
        #         result += '0'
        #         temp += message[i]
        #     else:
        #         r = temp - self.key
        #         if r == 0:
        #             temp = message[i]
        #             if (int(result) == 0):
        #                 result = ''
        #             result += '1'
        #         else:
        #             r = str(r).lstrip('0')
        #             result += '1'
        #             temp = r + message[i]
        # return r
        return self.key.encode()

    def encode(self, message):  # Message is a string, returns bytes
        return message.encode() + self.__gen_crc__(message)

    def decode(self, message):  # Message is bytes, returns a string
        recv_message = message[0:len(message) - len(self.key)]
        recv_crc = message[len(message) - len(self.key):len(message)]

        if (recv_crc == self.__gen_crc__(recv_message)):
            return recv_message.decode()

        raise Exception("Invalid message received")


crc = CRC()
input_message = "GraceIsCute"
print("Input message: " + input_message)
encoded_mess = crc.encode(input_message)
print("Encoded Message:" + str(encoded_mess))
decoded_mess = crc.decode(encoded_mess)
print(decoded_mess)
