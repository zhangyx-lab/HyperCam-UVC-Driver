from util.ASSERT import ASSERT


def normalizeInt(arg, range=None, name="Value"):
    if arg is None:
        return None
    val = int(arg)
    if range is not None:
        ASSERT(val >= range[0] and val <= range[1], f"{name} out of range")
    return val
