import settings as s

### Raspberry Pi Constants ###
M0 = 22
M1 = 27
SERIAL_NUM = "/dev/ttyS0"

### SX 1262 Constants ###
SX126X_UART_BAUDRATE_1200 = 0x00
SX126X_UART_BAUDRATE_2400 = 0x20
SX126X_UART_BAUDRATE_4800 = 0x40
SX126X_UART_BAUDRATE_9600 = 0x60
SX126X_UART_BAUDRATE_19200 = 0x80
SX126X_UART_BAUDRATE_38400 = 0xA0
SX126X_UART_BAUDRATE_57600 = 0xC0
SX126X_UART_BAUDRATE_115200 = 0xE0

SX126X_PACKAGE_SIZE_240_BYTE = 0x00
SX126X_PACKAGE_SIZE_128_BYTE = 0x40
SX126X_PACKAGE_SIZE_64_BYTE = 0x80
SX126X_PACKAGE_SIZE_32_BYTE = 0xC0

SX126X_Power_22dBm = 0x00
SX126X_Power_17dBm = 0x01
SX126X_Power_13dBm = 0x02
SX126X_Power_10dBm = 0x03

### Lora Constants ###
# start and offset frequencies of two lora modules
#
# E22-400T22S           E22-900T22S
# 410~493MHz      or    850~930MHz
FREQ = 915

# Air Speed (I *THINK* this is bit rate (kbps))
# TODO: try higher air speed
LORA_AIR_SPEED_DIC = {
    1200: 0x01,
    2400: 0x02,
    4800: 0x03,
    9600: 0x04,
    19200: 0x05,
    38400: 0x06,
    62500: 0x07
}
AIR_SPEED = LORA_AIR_SPEED_DIC.get(s.AIR_SPEED)

# Transmission Power (10,13,17,22) in dB
LORA_POWER_DIC = {
    22: SX126X_Power_22dBm,
    17: SX126X_Power_17dBm,
    13: SX126X_Power_13dBm,
    10: SX126X_Power_10dBm
}
POWER = LORA_POWER_DIC.get(s.POWER)
# UART Buffer Size
LORA_BUF_SZ_DIC = {
    240: SX126X_PACKAGE_SIZE_240_BYTE,
    128: SX126X_PACKAGE_SIZE_128_BYTE,
    64: SX126X_PACKAGE_SIZE_64_BYTE,
    32: SX126X_PACKAGE_SIZE_32_BYTE
}
BUF_SZ = LORA_BUF_SZ_DIC.get(s.BUF_SZ)

# RSSI (receive signal strength indicator)
RSSI = s.RSSI
RSSI_VAL = 0x80 if RSSI else 0x00

# DODO: add in WOR cycle