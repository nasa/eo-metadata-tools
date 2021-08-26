"""
This code has nothing to do with any ticket, it's just cool and everyone should
know how to send terminal colors to make their output more readable.

One usage is to display output from destructive calls in red, new data in green,
info in blue.

Enjoy
"""

# There are many colors, but these allow you to do red/green/blue or red/yellow/green
code_red = "\033[0;31m"
code_green ='\033[0;32m'
code_yellow ='\033[0;33m'
code_blue ='\033[0;34m'

code_bold = '\033[1m'
code_underline = '\033[4m'
code_warning = '\033[93m'
code_fail = '\033[91m'
code_header = '\033[95m'

code_none = "\033[0m"

def red(msg):
    return style_text(msg, code_red)

def green(msg):
    return style_text(msg, code_green)

def blue(msg):
    return style_text(msg, code_blue)

def yellow(msg):
    return style_text(msg, code_yellow)

def style_text(msg, color):
    return color + msg + code_none

print ("Primary Colors: %s %s %s." % (red("Red"), green("Green"), blue("Blue")))
print ("Traffic Lights: %s %s %s." % (red("stop"), yellow("faster"), green("go")))
print ("Test: %s, %s, %s, %s, %s." % (style_text("bold", code_bold),
    style_text("underline", code_underline),
    style_text("warning", code_warning),
    style_text("fail", code_fail),
    style_text("header", code_header)))
