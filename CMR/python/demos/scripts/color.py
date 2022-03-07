"""
This code has nothing to do with any ticket, it's just cool and everyone should
know how to send terminal colors to make their output more readable.

One usage is to display output from destructive calls in red, new data in green,
info in blue.

Enjoy
"""

# There are many colors, but these allow you to do red/green/blue or red/yellow/green

from enum import Enum

class Code(Enum):
    """ Terminal codes """
    RED = "\033[0;31m"
    GREEN ="\033[0;32m"
    YELLOW ="\033[0;33m"
    BLUE ="\033[0;34m"

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    HEADER = "\033[95m"

    NONE = "\033[0m"

def red(msg):
    "return red text"
    return style_text(msg, Code.RED)

def green(msg):
    "return green text"
    return style_text(msg, Code.GREEN)

def blue(msg):
    "return blue text"
    return style_text(msg, Code.BLUE)

def yellow(msg):
    "return yellow text"
    return style_text(msg, Code.YELLOW)

def style_text(msg, color):
    "returned text with terminal codes"
    return str(color.value) + msg + str(Code.NONE.value)

print (f'Primary Colors: {red("Red")} {green("Green")}  {blue("Blue")}')
print (f'Traffic Lights: {red("stop")} {yellow("faster")} {green("go")}')
print (f'Test: {style_text("bold", Code.BOLD)}, '
    f'{style_text("underline", Code.UNDERLINE)}, '
    f'{style_text("warning", Code.WARNING)}, '
    f'{style_text("fail", Code.FAIL)}, '
    f'{style_text("header", Code.HEADER)}')
