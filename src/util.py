from bitarray import bitarray
import binascii


def BER(input1: bytes, input2: bytes) -> float:
    array1 = bitarray()
    array1.frombytes(input1)
    array2 = bitarray()
    array2.frombytes(input2)
    if (len(array1) != len(array2)):
        raise Exception("Unequal Lengths")
    result = array1 ^ array2
    return float(result.count(1)) / float(len(result))


def formatBytes(input: bytes) -> str:
    return str(binascii.hexlify(bytearray(input)))
