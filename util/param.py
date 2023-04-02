# Python Modules
from __future__ import annotations
from typing import NamedTuple
from io import TextIOWrapper
import math
# PIP Packages
import numpy as np
# Range limits
RANGE = {
    "EXP": [50, 150],
    "LED": [1, 8],
    "PWM": [0, 255],
    "GAIN": [0, 100]
}


class PeakData(NamedTuple):
    target: float
    previous: float
    current: float

    def validate(self) -> tuple[bool, int]:
        def decline():
            d = self.target - self.current
            return False, int(np.sign(d))
        if self.previous is None:
            return decline()
        # Calculate relationship of the two samples
        delta = np.array([self.previous, self.current]) - self.target
        # Two samples on different sides, validation successful
        if delta[0] * delta[1] < 0:
            return True, np.argmin(np.abs(delta))
        else:
            return decline()


class CaptureDescriptor(NamedTuple):
    led: int
    pwm: int
    exp: int
    gain: int
    stack: int

    def adjust(self, val: int) -> CaptureDescriptor:
        if val > 0:
            if self.pwm < RANGE["PWM"][1]:
                # First try to increase led pwm
                return self._replace(
                    pwm=int(np.min([self.pwm + val, RANGE["PWM"][1]]))
                )
            elif self.exp < RANGE["EXP"][1]:
                # Try to increase exposure
                return self._replace(
                    exp=int(np.min([self.exp + val, RANGE["EXP"][1]]))
                )
            elif self.gain < RANGE["GAIN"][1]:
                # Last resort: try to increase gain
                return self._replace(
                    gain=int(np.min([self.gain + val, RANGE["GAIN"][1]]))
                )
            else:
                return None
        elif val < 0:
            if self.exp > RANGE["EXP"][0]:
                # First try to decrease exposure
                return self._replace(
                    exp=int(np.max([self.exp + val, RANGE["EXP"][0]]))
                )
            elif self.pwm > RANGE["PWM"][0]:
                # Try to decrease led pwm
                return self._replace(
                    pwm=int(np.max([self.pwm + val, RANGE["PWM"][0]]))
                )
            elif self.gain > RANGE["GAIN"][0]:
                # Last resort: try to increase gain
                return self._replace(
                    gain=int(np.max([self.gain + val, RANGE["GAIN"][0]]))
                )
            else:
                return None
        else:
            return None
        
    def matchGain(self, current, target) -> CaptureDescriptor:
        if current > target:
            # Do nothing
            return None
        elif current == target:
            return self
        else:
            delta_bri = target - current
            gain = 1000 * delta_bri / current
            return self._replace(gain=math.floor(gain))

    def write(self, file: TextIOWrapper):
        file.writelines([
            # f"led   = {self.led}\n",
            f"pwm   = {self.pwm}\n",
            f"exp   = {self.exp}\n",
            f"gain  = {self.gain}\n",
            # f"stack = {self.stack}\n",
        ])

    def __str__(self):
        l = [
            f"LED {self.led}",
            f"PWM {self.pwm}",
            f"EXP {self.exp}"
        ]
        if int(self.gain) > 0:
            l +=  [f"GAIN {self.gain}"]
        if int(self.stack) > 1:
            l += [f"STACK {self.stack}"]
        return ", ".join(l)


CaptureDescriptor.__new__.__defaults__ = (None, 0xFF, 0, 0, 1)


CALIB_INIT: list[CaptureDescriptor] = [
    None,
    CaptureDescriptor(pwm=0x00, exp=50),  # UV
    CaptureDescriptor(pwm=0x00, exp=50),  # BLUE
    CaptureDescriptor(pwm=0x00, exp=50),  # GREEN
    CaptureDescriptor(pwm=0xFF, exp=50),  # YG
    CaptureDescriptor(pwm=0x00, exp=50),  # YELLOW
    CaptureDescriptor(pwm=0x00, exp=50),  # ORANGE
    CaptureDescriptor(pwm=0x00, exp=50),  # RED
    CaptureDescriptor(pwm=0x00, exp=50),  # IR
]
