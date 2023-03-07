from reedsolo import RSCodec
from bitarray import bitarray
import math
import binascii

class ReedSoloman:
    max_block_len = 255 # perform individual rsc on each block in the message

    def __init__(self, block_len: int = max_block_len, max_corrections: int = 4):
        self.block_len = min(block_len, self.max_block_len) # this is max
        self.max_corrections = max_corrections
        self.block_rsc_len = 2*max_corrections
        self.reedsolo = RSCodec(self.block_rsc_len)
        self.enc_block_len = self.block_len + self.block_rsc_len # this is max
    
    def __bitarrayString__(self, msg: bytes) -> str:
        return str(binascii.hexlify(bytearray(msg)))
    
    def __num_blocks(self, input_len: int) -> int:
        return math.ceil(float(input_len) / self.block_len)
    
    def rsc_len(self, input_len: int) -> int:
        return self.__num_blocks(input_len) * self.block_rsc_len
            
    def __gen_rsc__(self, block: bytes) -> bytes:
        if len(block) > self.block_len:
            raise Exception("Must ensure maximum block length is met")
        return self.reedsolo.encode(block)

    def encode(self, message: bytes) -> bytes:
        result:bytes = b''
        num_blocks = self.__num_blocks(len(message))
        for i in range(num_blocks):
            result += self.__gen_rsc__(message[i*self.block_len:min((i+1)*self.block_len, len(message))])
        return result

    def decode(self, message: bytes) -> bytes:
        result:bytes = b''
        num_blocks = math.ceil(float(len(message)) / (self.enc_block_len))
        fixed_errors = 0
        try:
            for i in range(num_blocks):
                msg, _, errata_pos = self.reedsolo.decode(message[i*self.enc_block_len:min((i+1)*self.enc_block_len, len(message))])
                result += msg
                if len(list(errata_pos)) != 0:
                    fixed_errors += len(list(errata_pos))
        except Exception as e:
            raise Exception("Invalid message received")
        
        if fixed_errors > 0:
            print(f'Fixed {fixed_errors} errors during the decoding')
        return result
    
    
def rsc_test1():
    rsc = ReedSoloman()
    input_message: str = "TestSendingARandomMessageToEnsureTheCrcIsWorking"
    encoded_input:bytes = input_message.encode()
    rsc_encoded_input:bytes = rsc.encode(encoded_input)
    rsc_decoded_input:bytes = rsc.decode(rsc_encoded_input)
    successful_encoding:bool = encoded_input == rsc_decoded_input
    if successful_encoding:
        print("Successful crc encode&decode!")
    else:
        print("Unsuccessful crc encode&decode")
        
def rsc_test2():
    rsc = ReedSoloman()
    input_message: str = "TestSendingARandomMessageToEnsureTheCrcIsWorking"
    encoded_input:bytes = input_message.encode()
    rsc_encoded_input:bytes = rsc.encode(encoded_input)
    
    bits = bitarray()
    bits.frombytes(rsc_encoded_input)
    
    for i in [1, 10, 55]:
        bits[i] = 1 if bits[i] == 0 else 0
        
    encoded_error_input = bits.tobytes()
    try:
        rsc_decoded_input:bytes = rsc.decode(encoded_error_input)
        print("Fixed all errors, successfully")
        successful_encoding:bool = encoded_input == rsc_decoded_input
        if successful_encoding:
            print("Successful crc encode&decode!")
        else:
            print("Unsuccessful crc encode&decode")
    except:
        print("Did not fix errors successfully")
        
def rsc_test3():
    rsc = ReedSoloman()
    input_message: str = "TestSendingARandomMessageToEnsureTheCrcIsWorking"
    encoded_input:bytes = input_message.encode()
    rsc_encoded_input:bytes = rsc.encode(encoded_input)
    
    bits = bitarray()
    bits.frombytes(rsc_encoded_input)
    
    for i in [0, 10, 20, 30, 40]:
        bits[i] = 1 if bits[i] == 0 else 0
        
    encoded_error_input = bits.tobytes()
    try:
        rsc.decode(encoded_error_input)
        print("Did not detect error")
    except:
        print("Detected error successfully")
# rsc_test1()
# rsc_test2()
# rsc_test3()