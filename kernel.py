# The Python OS project #
import ast
import ctypes
import os
import sys
import msvcrt
from time import strftime, gmtime, time

from klib import kcolor
from klib import kcrypto
from klib import commandparser

# Define some constants #
KERNEL32 = ctypes.WinDLL("kernel32")
CRYPTO = kcrypto.Crypto
CPARSER = commandparser
LOGTIME = strftime("%Y_%m_%d-%H%M%S", gmtime(time()))

# Define base kernel functions and structs #
type Number = float | int


def IsDir(path: str) -> bool:
    path: ctypes.c_wchar_p = ctypes.c_wchar_p(path)
    result: int = KERNEL32.GetFileAttributesW(path)
    if result != -1 and result & 0x10:
        return True
    else:
        return False


class FileSystem:
    @staticmethod
    def CreateFile(filepath: str, data: bytes) -> None:
        with open(filepath, "wb") as FH:
            FH.write(data)

    @staticmethod
    def ReadFile(filepath: str) -> bytes:
        with open(filepath, "rb") as FH:
            return FH.read()

    @staticmethod
    def CopyFile(filepath: str, newpath: str) -> bool:
        source: ctypes.c_wchar_p = ctypes.c_wchar_p(filepath)
        destination = ctypes.c_wchar_p(newpath)

        filecopy: bool = KERNEL32.CopyFileW(source, destination, False)
        if filecopy:
            return True
        else:
            return False

    @staticmethod
    def DeleteAny(filepath: str) -> None:
        if IsDir(filepath):
            os.rmdir(filepath)
        else:
            os.remove(filepath)

    @staticmethod
    def CreateDirectory(dirpath: str) -> None:
        os.mkdir(dirpath)

    @staticmethod
    def ChangeDir(dirpath: str) -> None:
        os.chdir(dirpath)

    @staticmethod
    def ListDir(dirpath: str) -> list[str]:
        return os.listdir(dirpath)


class Char:
    def __init__(self, char: str):
        if len(char) == 1:
            self.CHAR: str = char
        else:
            raise TypeError

    def __str__(self):
        return self.CHAR


def PutChar(char: Char) -> None:
    print(str(char), end="")


def PutString(CharArray: list) -> None:
    for char in CharArray:
        PutChar(Char(char))


def PutCharFL(char: Char) -> None:
    print(str(char), end="", flush=True)


def PutStringFL(CharArray: list) -> None:
    for char in CharArray:
        PutCharFL(Char(char))


class stdio:
    @staticmethod
    def ReadChar() -> bytes:
        Rc: bytes = msvcrt.getche()
        return Rc

    @staticmethod
    def ReadLine() -> str:
        line = []
        while True:
            char = msvcrt.getche()
            if char in b'\r\n':  # Check for Enter key (carriage return or newline)
                print()  # Print newline for user feedback
                return ''.join(line)
            line.append(char.decode('utf-8'))

    @staticmethod
    def ReadCharNE() -> bytes:
        Rc: bytes = msvcrt.getch()
        return Rc

    @staticmethod
    def ReadLineNE() -> str:
        line = []
        while True:
            char = msvcrt.getch()
            if char in b'\r\n':  # Check for Enter key (carriage return or newline)
                print()  # Print newline for user feedback
                return ''.join(line)
            line.append(char.decode('utf-8'))

    @staticmethod
    def cprint(text: str, attributes: list[bool | int]):
        kcolor.cprint(text, *attributes)

    @staticmethod
    def Choice(__prompt: str = "(Y/n)? ", choices: list[str] = None, lower: bool = True):
        choices = ["y", "n"] if choices is None else choices
        choice = input(__prompt)
        for _choice in choices:
            if choice.lower() if lower else choice == _choice:  # Should choice be lowercase or not
                # depending on argument bool then check if the choice is equal to the selected choice by the loop.
                return _choice  # Return that choice so the program can process it accordingly.
        else:
            return None


class Types:
    class ParserError(BaseException):
        def __init__(self, ExceptionMessage: str = "Parser error!"):
            self.message = ExceptionMessage
            super().__init__(self.message)

    @staticmethod
    def ParseInt(x: str, to: object):
        to = int(x)

    def ParseString(self, x: str, to: object):
        if x.lower() == "false" or x.lower() == "true":
            to = bool(x)
        elif x.lower() == "none":
            to = None
        elif "1234567890" in x.lower():
            to = int(x)
        elif isinstance(x, str):
            to = x
        else:
            raise self.ParserError(f"Unable to convert string to valid type.")


def field_7889_f(var1):
    """Undocumented"""
    p_0001_7889f = "("
    p_0002_7889f = ()
    p_0003_7889f = []
    for b in var1:
        if isinstance(b, str):
            p_0003_7889f.append("'"+b+"'")
            continue
        p_0003_7889f.append(b)
    for b, a in enumerate(p_0003_7889f):
        p_0001_7889f = p_0001_7889f + str(a)
        if b == len(var1) - 1:
            pass
        else:
            p_0001_7889f = p_0001_7889f + ","
    p_0001_7889f = p_0001_7889f + ")"
    p_0002_7889f = ast.literal_eval(p_0001_7889f)
    return p_0002_7889f


if __name__ == '__main__':
    field_7889_f([["77", 77], 78, "e9", True])
