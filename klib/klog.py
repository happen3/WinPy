from klib import kcolor
from klib.pkmgr import interface__CPRINT
from time import time, gmtime, strftime
from klib import filewriter
import kernel


class Logged:
    def __init__(self, message: str = "Message.", loglvl: int = 0):
        self.msg = message
        self.loglvl = loglvl

    def log(self):
        interface__CPRINT(self.msg, [0x07, 0x00] if self.loglvl == 0 else [0x0e, 0x00] if self.loglvl == 1 else [0x0c,
                                                                                                                 0x00])


class LoggedFile:
    def __init__(self, message: str = "Message.", loglvl: int = 0):
        self.msg = message
        self.loglvl = loglvl

    def log(self):
        with filewriter.ContinuousLogWriter(kernel.LOGTIME + ".log") as FH:
            filewriter.fprintf(
                ("[INFO]: " if self.loglvl == 0 else "[WARN]: " if self.loglvl == 1 else "[ERROR]: ") + self.msg,
                FH
            )
