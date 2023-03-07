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


def genLongLoremIpsom() -> str:
    return  """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Dignissim convallis aenean et tortor. Suspendisse sed nisi lacus sed viverra tellus. Nisl condimentum id venenatis a. Sociis natoque penatibus et magnis dis parturient. Egestas maecenas pharetra convallis posuere morbi leo urna. Pharetra et ultrices neque ornare aenean euismod elementum nisi quis. Eget felis eget nunc lobortis mattis aliquam faucibus purus in. Amet dictum sit amet justo donec enim. Consectetur libero id faucibus nisl. In metus vulputate eu scelerisque felis imperdiet proin fermentum. Orci dapibus ultrices in iaculis nunc sed augue lacus. Fusce ut placerat orci nulla pellentesque dignissim enim. Viverra accumsan in nisl nisi scelerisque eu ultrices vitae. Sed augue lacus viverra vitae congue eu consequat ac felis.
        Enim nec dui nunc mattis enim. Scelerisque mauris pellentesque pulvinar pellentesque. Adipiscing bibendum est ultricies integer quis. A diam sollicitudin tempor id eu nisl nunc mi. Purus ut faucibus pulvinar elementum integer enim neque. Mauris augue neque gravida in fermentum et sollicitudin. Aliquam nulla facilisi cras fermentum odio. Pharetra pharetra massa massa ultricies mi quis hendrerit dolor magna. In fermentum posuere urna nec tincidunt praesent semper feugiat. Aenean pharetra magna ac placerat. Aliquam vestibulum morbi blandit cursus risus at. Vitae semper quis lectus nulla at volutpat diam ut. Ultrices vitae auctor eu augue ut. Egestas purus viverra accumsan in nisl nisi scelerisque. Cursus risus at ultrices mi tempus imperdiet nulla. Mattis enim ut tellus elementum sagittis vitae.
        Erat velit scelerisque in dictum non. Dictumst vestibulum rhoncus est pellentesque elit ullamcorper dignissim cras tincidunt. Adipiscing elit pellentesque habitant morbi tristique senectus et netus. Dui faucibus in ornare quam viverra orci. Enim neque volutpat ac tincidunt vitae semper quis lectus. Aliquet nec ullamcorper sit amet risus nullam eget felis. Libero nunc consequat interdum varius sit. Sit amet cursus sit amet dictum sit amet. A diam sollicitudin tempor id eu nisl nunc mi ipsum. Sed vulputate mi sit amet mauris commodo quis imperdiet massa. Mauris commodo quis imperdiet massa tincidunt nunc. In aliquam sem fringilla ut morbi tincidunt augue interdum. Nulla at volutpat diam ut. Tortor posuere ac ut consequat semper viverra nam libero. Tellus at urna condimentum mattis. Congue quisque egestas diam in.
        Cras ornare arcu dui vivamus. Sed tempus urna et pharetra pharetra. Massa sapien faucibus et molestie ac feugiat. Egestas erat imperdiet sed euismod nisi porta lorem. Mi proin sed libero enim sed faucibus. Diam maecenas sed enim ut sem viverra. Turpis massa tincidunt dui ut ornare lectus sit amet. Vitae aliquet nec ullamcorper sit amet risus nullam. Mauris cursus mattis molestie a. Curabitur vitae nunc sed velit dignissim sodales ut eu sem. Quis vel eros donec ac odio tempor orci dapibus ultrices. Neque viverra justo nec ultrices dui sapien eget mi. Urna neque viverra justo nec ultrices. Gravida rutrum quisque non tellus orci. Sem nulla pharetra diam sit amet nisl suscipit adipiscing. Nibh mauris cursus mattis molestie a.
        Mauris cursus mattis molestie a iaculis at erat pellentesque adipiscing. Odio morbi quis commodo odio aenean sed adipiscing. Ut sem viverra aliquet eget sit amet. Vel fringilla est ullamcorper eget nulla facilisi. Vitae proin sagittis nisl rhoncus. Iaculis at erat pellentesque adipiscing commodo elit at. Suscipit adipiscing bibendum est ultricies. Elit eget gravida cum sociis natoque penatibus. Quis vel eros donec ac odio. Amet est placerat in egestas erat imperdiet sed. Bibendum neque egestas congue quisque egestas diam in arcu cursus. Tortor id aliquet lectus proin nibh. In fermentum posuere urna nec. Faucibus turpis in eu mi bibendum neque egestas congue quisque. Aliquam etiam erat velit scelerisque in dictum. Facilisis leo vel fringilla est. Purus sit amet luctus venenatis lectus. Dignissim enim sit amet venenatis urna cursus eget nunc. 
        Nascetur ridiculus mus mauris vitae ultricies leo integer malesuada.i9650GgbH7xsjSr3FO1BKZo01YXGwFU8fE62fSc6w9AZMiXJvtBPc3iMr8W3PvFI54aSP4MDNJpBk25EKs5TJJA66sX7pKzZ1Y4XGCiw06HY1YG6v9Gg1Y3yP952hF8HkSRksQTd5j09ml0XX554um7gCUMXSHDv28wkKR7eOTq3N0jAZPI2n330mixIL"""
        
def gen_packet(length: int = 219) -> str:
    base_msg = f'Temp is {get_cpu_temp()} deg C. Long Tail Message: {genLongLoremIpsom()}'
    if len(base_msg) < length:
        base_msg += genLongLoremIpsom()
    return base_msg[:length]