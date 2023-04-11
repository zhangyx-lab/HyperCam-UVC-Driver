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
from util.param import PeakData, CaptureDescriptor, CALIB_INIT, RANGE



def clearCam(threshold: float = 0.2):
    serial_write(SOFT_RST)
    while peakBrightness(capture(1, 0, 0)) >= threshold:
        cprint("Peak brightness", peakBrightness(capture(1, 0, 0)))
        pass


def directCapture(desc: CaptureDescriptor) -> np.ndarray:
    cprint(f"Capture: {desc}")
    serial_write(SOFT_RST, [desc.led, desc.pwm])
    manualExposure.set(desc.exp)
    desc.write()
    frame = capture(desc.stack, desc.gain, 1)
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
    serial_write(SOFT_RST)
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
            elif peak.current > peak.target:
                # Tune the peak back to just lower than target
                peak = peak._replace(previous=None)
                prev_desc = None
                prev_frame = None
            else:
                result = (
                    desc.matchGain(peak.current, peak.target)
                    or
                    prev_desc.matchGain(peak.previous, peak.target)
                )
                cprint(f"Calibration done: {result}")
                result.write()
                manualExposure.set(desc.exp)
                frame = capture(result.stack, result.gain)
                cprint(f"Final result peak brightness {peakBrightness(frame)}")
                return frame if val else prev_frame
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


preview_ae = 10
preview_br = None

def fullBandPreview(stack: int = 1, peak_bri: float = 0.9):
    cprint("Entering Full Band Preview")
    # Turn on all LEDs that are harmless to human eyes
    serial_write(
        SOFT_RST,
        [1, 0x00],  # UV Disabled
        [2, 0x10],  # BLUE
        [3, 0x30],  # GREEN
        [4, 0x80],
        [5, 0x40],
        [6, 0x30],
        [7, 0x08],  # RED
        [8, 0x00],  # IR
    )
    # Determine next exposure value
    global preview_ae, preview_br
    if preview_br is not None:
        if preview_ae < peak_bri and preview_br < RANGE["EXP"][1]:
            preview_ae += 1
        elif preview_ae > peak_bri and preview_br > 1:
            preview_ae -= 1
    # Update exposure value
    manualExposure.set(preview_ae)
    frame = capture(1, 0, 0)
    preview_br = peakBrightness(frame)
    cprint(f"EXP {preview_ae}, peak_bri = {preview_br}")
    # Return this frame
    return frame
