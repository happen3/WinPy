import ctypes
from ctypes import wintypes
import sys

# Constants for Windows API
STD_OUTPUT_HANDLE = -11
FOREGROUND_BLACK = 0x00
FOREGROUND_BLUE = 0x01
FOREGROUND_GREEN = 0x02
FOREGROUND_RED = 0x04
FOREGROUND_YELLOW = FOREGROUND_RED | FOREGROUND_GREEN
FOREGROUND_INTENSITY = 0x08
BACKGROUND_BLACK = 0x00
BACKGROUND_BLUE = 0x10
BACKGROUND_GREEN = 0x20
BACKGROUND_RED = 0x40
BACKGROUND_YELLOW = BACKGROUND_RED | BACKGROUND_GREEN
BACKGROUND_INTENSITY = 0x80

# Functions from kernel32.dll
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
stdout_handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


def _set_text_color_(color):
    kernel32.SetConsoleTextAttribute(stdout_handle, color)


def _reset_text_color_():
    _set_text_color_(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)


def cprint(text, color=None, bg_color=None, bold=False, italic=False):
    attributes = 0

    if color:
        attributes |= color

    if bg_color:
        attributes |= bg_color

    if bold or italic:
        attributes |= FOREGROUND_INTENSITY

    _set_text_color_(attributes)
    sys.stdout.write(text + "\r\n")
    _reset_text_color_()


if __name__ == '__main__':
    # Example usage
    cprint("Normal Text")
    cprint("Bold Text", bold=True)
    cprint("Italic Text (simulated)", italic=True)
    cprint("Yellow Text on Blue Background", FOREGROUND_YELLOW, BACKGROUND_BLUE)
