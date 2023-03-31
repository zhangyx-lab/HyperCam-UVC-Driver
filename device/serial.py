# Python Modules
import atexit
# PIP Packages
from serial import Serial
# Project Packages
from util.env import hard_reset_on_exit, serial_device, locateDeviceOptional
from util.ASSERT import ASSERT

# Initialize LED serial device
path = locateDeviceOptional(serial_device, '/dev/ttyACM*')
serial = Serial(path)
ASSERT(serial.is_open, f"Unable to open serial device {path}")


def serial_write(*args: list[int]):
    payload = [0, 0]
    for arg in args:
        payload += arg
    serial.write(bytes(payload))


SOFT_RST = [0xFF, 0x00]
HARD_RST = [0xFF, 0xFF]

serial_write([0xFF, 0x00])

atexit.register(
    serial_write,
    HARD_RST if hard_reset_on_exit else SOFT_RST
)
