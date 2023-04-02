import numpy as np
from util.ASSERT import ASSERT


def peakBrightness(img: np.ndarray, r: list = [0.8, 0.9]) -> float:
    flat = np.sort(img.reshape((-1,)))
    l, r = np.rint(np.sort(r) * len(flat)).astype(np.uint)
    ASSERT(l >= 0 and r <= len(flat), f"Index out of range: <{l}, {r}>")
    flat = flat[l:r]
    if flat.dtype == np.uint8:
        flat = flat.astype(np.float32) / 0xFF
    if flat.dtype == np.uint16:
        flat = flat.astype(np.float32) / 0xFFFF
    elif flat.dtype != np.float32:
        flat = flat.astype(np.float32)
    bri_range = [float(f(flat)) for f in [np.max, np.min]]
    ASSERT(bri_range[0] >= 0 and bri_range[1] <= 1, f"Brightness out of range: {bri_range}")
    return np.average(flat)
    
