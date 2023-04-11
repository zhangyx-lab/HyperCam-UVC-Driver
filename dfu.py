#!python3
from device.serial import serial_write, DFU_MAGIC, HARD_RST, path
print(f"{path} : Entering DFU mode")
serial_write(DFU_MAGIC)
