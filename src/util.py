from bitarray import bitarray
import binascii
import csv


#    The following is to obtain the temprature of the RPi CPU
def get_cpu_temp() -> float:
    tempFile = open("/sys/class/thermal/thermal_zone0/temp")
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp) / 1000

def BER(input1: bytes, input2: bytes) -> float:
    array1 = bitarray()
    array1.frombytes(input1)
    array2 = bitarray()
    array2.frombytes(input2)
    if (len(array1) != len(array2)):
        raise Exception("Unequal Lengths")
    result = array1 ^ array2
    matching_bits = result.count(1)
    return (float(matching_bits) / float(len(result)), len(result),
            matching_bits)


def formatBytes(input: bytes) -> str:
    return str(binascii.hexlify(bytearray(input)))

def createOutputCSV (file_path: str, header: str) -> None:
    with open(file_path, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

def writeRXValuestoCSV(file_string, rec_values):
    with open(file_string, 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(rec_values)
