from util.env import command_template
from util.ASSERT import ASSERT


prev_kw = {}
frame = None


def kwargs(arg: str):
    global prev_kw
    ASSERT(arg is not None)
    if command_template is not None:
        arg = ';'.join([command_template, arg])
    kw = {}
    for param in arg.split(";"):
        param = [p.strip() for p in param.split("=", 1)]
        key = param[0]
        if key == "":
            return kw
        elif key == "!":
            return prev_kw
        elif len(param) == 1:
            kw[key] = None
        else:
            kw[key] = param[1]
    prev_kw = kw
    return kw