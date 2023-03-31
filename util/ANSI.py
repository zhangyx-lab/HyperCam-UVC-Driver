"""ANSI escape sequences"""


def ESCAPE(*CODE):
    return f"\033[{';'.join(map(str, CODE))}m"


def FORMAT(open=0, close=0):
    def F(*s, join=" "): return ESCAPE(open) + join.join(s) + ESCAPE(close)
    return F

class Color:
    def reset(): return ESCAPE(0)

    bold = FORMAT(1, 22)
    dim = FORMAT(2, 22)
    italic = FORMAT(3, 23)
    underline = FORMAT(4, 24)
    blink = FORMAT(5, 25)
    invert = FORMAT(7, 27)
    invisible = FORMAT(8, 28)
    strike = FORMAT(9, 29)

    grey = FORMAT(30)
    red = FORMAT(31)
    green = FORMAT(32)
    yellow = FORMAT(33)
    blue = FORMAT(34)
    purple = FORMAT(35)
    cyan = FORMAT(36)
    white = FORMAT(37)

    bgBlack = FORMAT(40)
    bgRed = FORMAT(41)
    bgGreen = FORMAT(42)
    bgYellow = FORMAT(43)
    bgBlue = FORMAT(44)
    bgPurple = FORMAT(45)
    bgCyan = FORMAT(46)
    bgWhite = FORMAT(47)

    brightGrey = FORMAT(90)
    brightRed = FORMAT(91)
    brightGreen = FORMAT(92)
    brightYellow = FORMAT(93)
    brightBlue = FORMAT(94)
    brightPurple = FORMAT(95)
    brightCyan = FORMAT(96)
    brightWhite = FORMAT(97)

    bgBrightGray = FORMAT(100)
    bgBrightRed = FORMAT(101)
    bgBrightGreen = FORMAT(102)
    bgBrightYellow = FORMAT(103)
    bgBrightBlue = FORMAT(104)
    bgBrightPurple = FORMAT(105)
    bgBrightCyan = FORMAT(106)
    bgBrightWhite = FORMAT(107)
