#!python3
# Python Modules
import sys
import cv2
import time
# Project packages
from util.env import WIN_NAME, command
from util.norm import normalizeInt
from util.print import cprint
from util.kwargs import kwargs
from util.param import RANGE
from util.param import CaptureDescriptor
import util.execute


frame = None


def execute(out=None, exp=None, led=None, pwm=None, gain=0, stack=0, peak_bri=0.9):
    global frame
    desc = CaptureDescriptor(
        led=normalizeInt(led, RANGE["LED"], "LED index"),
        pwm=normalizeInt(pwm, RANGE["PWM"], "PWM"),
        exp=normalizeInt(exp, RANGE["EXP"], "Exposure"),
        gain=normalizeInt(gain, RANGE["GAIN"], "Gain"),
        stack=normalizeInt(stack, [0, 0xFF], "Stack")
    )
    # Perform capture
    if desc.led is None:
        frame = util.execute.fullBandPreview(stack)
    elif desc.exp is None or desc.pwm is None:
        frame = util.execute.calibrateExposure(desc, peak_bri)
    else:
        frame = util.execute.directCapture(desc)
    # Check for frame availablity
    if frame is None:
        return
    # Send the frame to its destination
    if WIN_NAME is not None:
        cv2.imshow(WIN_NAME, frame)
        cv2.waitKey(1)
    if out is not None:
        cv2.imwrite(out, frame)


if command is not None:
    execute(**kwargs(command))
else:
    print("[READY]")
    while True:
        line = sys.stdin.readline()
        if len(line) == 0:
            break
        else:
            line = line[:-1]
        time_start = time.time_ns()
        execute(**kwargs(line))
        time_end = time.time_ns()
        print("[COMPLETE]")
        duration = float(time_end - time_start) / 1e6
        cprint(f"Execution time: {duration}ms")


if WIN_NAME is not None:
    cprint("Press anykey to exit")
    if util.execute.user_key[0] < 0:
        cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.waitKey(1)
