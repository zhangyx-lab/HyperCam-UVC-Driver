# PIP Packages
import numpy as np
import cv2
# Project Packages
from util.env import WIN_NAME, video_device, locateDeviceOptional
from util.print import cprint
from util.ASSERT import ASSERT
from util.session import Session
# Initialize camera device
V_PATH = locateDeviceOptional(video_device, '/dev/video*')
camera = cv2.VideoCapture(V_PATH)
ASSERT(camera.isOpened(), f"Cannot capture from device {V_PATH}")


user_key = [-1]


def camera_configure(prop: int, val: float, name: str = None, crash: bool = True):
    # Normalize arguments
    val = float(val)
    if name is None:
        name = f"CV_PROPORTY({prop})"
    # Configure the camera
    ret = camera.set(prop, val)
    new_val = camera.get(prop)
    # Check for retval
    ASSERT(
        ret == True,
        f"Proproty {name} is NOT supported by this camera",
        crash=crash
    )
    # Check for new prop val
    ASSERT(
        new_val == val,
        f"Failed to set {name} to {val} (current value = {new_val})",
        crash=crash
    )
    # Return updated value
    return new_val


class ManualExposure:
    enabled = False

    def __init__(self) -> None:
        current_mode = camera.get(cv2.CAP_PROP_AUTO_EXPOSURE)
        self.enabled = int(current_mode) == 1

    def mode_name(self, val) -> str:
        if val == 1:
            return "[MANUAL]"
        elif val == 3:
            return "[AUTO]"
        else:
            return "[UNKNOWN]"

    def disable(self, *args, **kwargs):
        cprint("Disabling auto exposure")
        camera_configure(cv2.CAP_PROP_AUTO_EXPOSURE, 3, "AUTO_EXPOSURE")
        self.enabled = False
        return Session(exit=self.enable)

    def enable(self, *args, **kwargs):
        cprint("Enabling auto exposure")
        camera_configure(cv2.CAP_PROP_AUTO_EXPOSURE, 1, "AUTO_EXPOSURE")
        self.enabled = True
        return Session(exit=self.disable)

    def set(self, val: int):
        if not self.enabled:
            self.enable()
        camera_configure(cv2.CAP_PROP_EXPOSURE, val)


def camera_read() -> np.ndarray:
    ret, frame = camera.read()
    ASSERT(ret, "Failed to read from camera")
    return frame


def capture(stack: int = 1, gain: int = 0, grab: int = 0) -> np.ndarray:
    ASSERT(stack >= 0, f"Illegal stack number {stack}")
    # Remove current frame
    for _ in range(grab):
        camera.grab()
    if stack == 0:
        return np.zeros(frame_size, dtype=np.uint16)
    stack = np.concatenate([camera_read() for _ in range(int(stack))], axis=2)
    img = np.average(stack, axis=2)
    scale = 0xFF * (1.0 + gain / 1000)
    img = np.rint(img * scale).astype(np.uint16)
    if WIN_NAME is not None:
        cv2.imshow(WIN_NAME, img)
        user_key[0] = cv2.waitKey(1)
    return img


# Camera defaults to manual exposure
manualExposure = ManualExposure()
# Important: disables the internal buffer of the camera
camera_configure(cv2.CAP_PROP_BUFFERSIZE, 1, "BUFFER_SIZE")
camera_configure(cv2.CAP_PROP_SHARPNESS, 0, "SHARPNESS", crash=False)
camera_configure(cv2.CAP_PROP_BACKLIGHT, 0, "BACKLIGHT", crash=False)
camera_configure(cv2.CAP_PROP_GAIN, 0, "GAIN", crash=False)
camera_configure(cv2.CAP_PROP_MODE, 0, "MODE", crash=False)
camera_configure(
    cv2.CAP_PROP_FOURCC,
    cv2.VideoWriter_fourcc(*"MJPG"),
    "FOURCC",
    crash=False
)
camera_configure(cv2.CAP_PROP_FPS, 50, "FPS", crash=False)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
camera_configure(cv2.CAP_PROP_FRAME_HEIGHT, 1200)


frame_size = (
    int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)),
    int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
)

cprint("Frame Size", frame_size)

if WIN_NAME is not None:
    cv2.startWindowThread()
    cv2.namedWindow(WIN_NAME)
    cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_TOPMOST, 1)
    cv2.setWindowProperty(WIN_NAME, cv2.WND_PROP_AUTOSIZE, 1)
    cv2.imshow(WIN_NAME, np.zeros(frame_size, dtype=np.uint8))
    cv2.waitKey(1)
# Grab one image from the device
camera.grab()
