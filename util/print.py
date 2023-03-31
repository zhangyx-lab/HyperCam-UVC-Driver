from sys import stderr
from util.ANSI import Color


def COMMENT(lines: list, join=" ") -> str:
    lines = join.join(map(str, lines)).split("\n")
    return "\n".join(["# " + str(l) for l in lines])


if stderr.isatty():

    def eprint(*lines, join=" ", color=Color.brightRed):
        """Print error messages"""
        print(color(join.join(map(str, lines))), file=stderr)

    def cprint(*lines, join=" ", color=Color.brightBlue):
        """Print comments"""
        print(color(COMMENT(lines, join=join)), file=stderr)

else:

    def eprint(*lines, join=" ", color=None):
        """Print error messages"""
        print(join.join(map(str, lines)), file=stderr)

    def cprint(*lines, join=" ", color=None):
        """Print comments"""
        print(COMMENT(lines, join=join), file=stderr)
