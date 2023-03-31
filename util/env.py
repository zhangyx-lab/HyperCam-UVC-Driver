from os import getcwd, mkdir
from os.path import dirname, exists
from argparse import ArgumentParser
from glob import glob
from pathlib import Path
# Project Packages
from util.ASSERT import ASSERT
from util.print import cprint


PROJECT_HOME = Path(dirname(dirname(__file__)))
cprint("Project directory:", PROJECT_HOME)
WORK_DIR = Path(getcwd())
cprint("Working directory", WORK_DIR)
VAR = PROJECT_HOME / "var"


def ensureDir(path):
    cprint("ENSURE", path)
    if not exists(path):
        mkdir(path)


for d in [VAR]:
    ensureDir(d)


def locateDeviceOptional(arg, matcher: str) -> str:
    if arg is not None:
        return arg
    l = list(glob(matcher))
    l.sort()
    ASSERT(len(l) > 0, f"Unable to locate device by {matcher}")
    return l[0]


parser = ArgumentParser()
parser.add_argument('-p', '--preview', default=False,
                    action='store_true', help="Enable preview window")
parser.add_argument('-R', '--hard-reset-on-exit', default=False,
                    action='store_true', help="Reset serial device on exit")
parser.add_argument('--window-name', default="Camera Preview",
                    type=str, help="Name of the preview window")
parser.add_argument('--video-device', default=None,
                    help="Full path to the video device (usually under /dev)")
parser.add_argument('--serial-device', default=None,
                    help="Full path to the LED device (usually under /dev)")
parser.add_argument('-T', '--template', default=None,
                    help="Command template prefixed to each line")
# positional argument
parser.add_argument('command', nargs='*', help="Run command and exit")
args = parser.parse_args()

WIN_NAME = args.window_name if args.preview else None

hard_reset_on_exit = args.hard_reset_on_exit
video_device = args.video_device
serial_device = args.serial_device
command_template = args.template
command = "; ".join(args.command) if len(args.command) else None
if command is not None:
    cprint("Executing command:", command)
