# Python Modules
from sys import stdout
# PIP Packages
import numpy as np
# Project Packages
from device.camera import manualExposure, capture, user_key, camera
from device.serial import serial_write, SOFT_RST
from util.ASSERT import ASSERT
from util.env import WIN_NAME, VAR
from util.print import cprint
from util.img import peakBrightness
from util.param import PeakData, CaptureDescriptor, CALIB_INIT



def clearCam(threshold: float = 0.2):
    serial_write(SOFT_RST)
    while peakBrightness(capture(1, 0, 0)) >= threshold:
        cprint("Peak brightness", peakBrightness(capture(1, 0, 0)))
        pass


def directCapture(desc: CaptureDescriptor) -> np.ndarray:
    cprint(f"Capture: {desc}")
    serial_write(SOFT_RST)
    manualExposure.set(desc.exp)
    serial_write([desc.led, desc.pwm])
    frame = capture(desc.stack, desc.gain, 10)
    # Reset the LED module before reutrning
    serial_write(SOFT_RST)
    return frame


def calibrateExposure(desc: CaptureDescriptor, peak_bri: float) -> np.ndarray:
    cprint(f"Calibrating exposure for LED {desc.led}")
    peak = PeakData(target=peak_bri, previous=None, current=None)
    if desc.exp is None:
        desc = desc._replace(exp=CALIB_INIT[desc.led].exp)
    if desc.pwm is None:
        desc = desc._replace(pwm=CALIB_INIT[desc.led].pwm)
    prev_desc: CaptureDescriptor = None
    prev_frame: np.ndarray = None
    manualExposure.set(desc.exp)
    clearCam()
    while True:
        # Update parameters
        serial_write([desc.led, desc.pwm])
        manualExposure.set(desc.exp)
        # Capture frame
        frame = capture(desc.stack, desc.gain)
        # Check for brightness
        peak = peak._replace(current=peakBrightness(frame))
        cprint(f"Calibrate: {desc} => Peak {peak.current:.4f}")
        # Compare with previous
        # open(VAR / f"cal_led_{desc.led}.txt", "w")
        converge, val = peak.validate()
        if converge:
            if desc.stack < 10:
                # Set stack to 5 and fine tune the result
                desc = desc._replace(stack=10)
                peak = peak._replace(previous=None)
                prev_desc = None
                prev_frame = None
            elif val == 0:
                cprint(f"Calibration done: {prev_desc}")
                prev_desc.write(stdout)
                return prev_frame
            else:
                ASSERT(val == 1)
                cprint(f"Calibration done: {desc}")
                desc.write(stdout)
                return frame
        else:
            # Not yet converged
            ASSERT(val != 0)
            # Prepare for next iteration
            peak = peak._replace(previous=peak.current)
            prev_frame = frame
            prev_desc = desc
            # iterate descriptor
            desc = desc.adjust(val)
            if desc is None:
                ASSERT(
                    False,
                    f"Unable to converage, stopping at {prev_desc}",
                    crash=False
                )
                prev_desc.write()
                return prev_frame


def fullBandPreview(stack: int = 1):
    cprint("Entering Full Band Preview")
    # Turn on all LEDs that are harmless to human eyes
    serial_write(
        SOFT_RST,
        [1, 0x00],  # UV Disabled
        [2, 0x20],  # BLUE
        [3, 0x60],  # GREEN
        [4, 0xF0],
        [5, 0x80],
        [6, 0x60],
        [7, 0x10],  # RED
        [8, 0x10],  # IR
    )
    # Auto Exposure is enforced in this mode
    with manualExposure.disable():
        if WIN_NAME is not None:
            frame = None
            while user_key[0] < 0:
                frame = capture(stack, 0)
            return frame
        else:
            # Capture a frame
            return capture(stack)
