from os.path import relpath
from inspect import stack
from sys import stderr, exit
import util.env as env
from util.ANSI import Color
from util.print import cprint, eprint


def ASSERT(cond, message: str = "Assertion failed", crash: bool = True):
    if cond:
        return
    trace = stack()[1]
    filename = relpath(trace.filename, env.PROJECT_HOME)
    trace_message = f"{filename}:{trace.lineno}:{trace.index} {trace.function}"
    if stderr.isatty():
        trace_message = Color.underline(trace_message) + ':'
    if crash:
        eprint(trace_message, message)
        exit(1)
    else:
        cprint(trace_message, message, color=Color.brightYellow)
