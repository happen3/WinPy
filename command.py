import pickle
import shutil
import zipfile
import marshal

import kernel
from klib import commandparser
from klib import application
from klib import pkmgr
import os
import pathlib
from klib import klog

idx: int = 0
klog.LoggedFile("Starting up command line!").log()

if not pathlib.Path("path.sys").exists():
    SPATH = [".\\sbin\\"]
    with open("path.sys", "wb") as FH:
        marshal.dump(SPATH, FH)
else:
    with open("path.sys", 'rb') as FH:
        SPATH = marshal.load(FH)
CPRINT = kernel.stdio.cprint

import ctypes


def get_drive_info(drive_letter):
    # Convert drive letter to a form acceptable to GetVolumeInformationW
    drive_letter += ':\\'
    volume_name_buf = ctypes.create_unicode_buffer(1024)
    volume_serial_number = ctypes.c_ulonglong()
    max_component_length = ctypes.c_ulong()
    file_system_flags = ctypes.c_ulong()
    file_system_name_buf = ctypes.create_unicode_buffer(1024)

    # Call GetVolumeInformationW to retrieve volume information
    success = kernel.KERNEL32.GetVolumeInformationW(
        ctypes.c_wchar_p(drive_letter),
        volume_name_buf,
        ctypes.sizeof(volume_name_buf),
        ctypes.byref(volume_serial_number),
        ctypes.byref(max_component_length),
        ctypes.byref(file_system_flags),
        file_system_name_buf,
        ctypes.sizeof(file_system_name_buf)
    )

    if success:
        volume_name = volume_name_buf.value
        volume_serial = volume_serial_number.value
        file_system_name = file_system_name_buf.value
        return volume_name, volume_serial, file_system_name
    else:
        print(
            f"Failed to get information for drive {drive_letter}. Error code: {ctypes.windll.kernel32.GetLastError()}")
        return None, None, None


def get_drive_number(drive_letter):
    # Get bitmask of all logical drives
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()

    # Iterate over each drive letter (bit in bitmask) to find the matching drive
    drive_number = -1
    for i in range(26):  # 26 letters A-Z
        if bitmask & (1 << i):
            drive = chr(65 + i)  # Convert to drive letter (A=65, B=66, ..., Z=90)
            if drive.upper() == drive_letter.upper():
                drive_number = i
                break

    if drive_number == -1:
        print(f"Drive {drive_letter} not found.")

    return drive_number


CPRINT("## WinPy kernel ##\r", [0x0e, 0x00])
print()
while True:

    dev = get_drive_info(os.getcwd()[0])
    ddn = get_drive_number(os.getcwd()[0])
    ddn = "0" + str(ddn) if ddn <= 9 else str(ddn)

    prompt = input(f"\\mnt\\{str(dev[2]).lower() + str(ddn)}{os.getcwd()[2:]} >>> ")
    command: list[str] = commandparser.parse(prompt)
    if len(command) == 0:
        continue
    try:
        # Dangerous space
        try:
            if command[1] == ">":
                try:
                    with open(command[2], "w") as FH:
                        FH.write(command[0])
                except IndexError:
                    pass
                continue
        except IndexError:
            pass
        try:
            if pathlib.Path(f".\\sbin\\{command[0]}.kx").exists():
                application.execute_app(f".\\sbin\\{command[0]}.kx")
                continue
            if pathlib.Path(f".\\sbin\\{command[0]}.kxa").exists():
                with open(f".\\sbin\\{command[0]}.kxa", "rb") as FH:
                    app = pickle.load(FH)
                appcode = marshal.loads(app["_text_"])
                exec(appcode["code"])
                continue
            if pathlib.Path(f".\\sbin\\{command[0]}.pkg").exists():
                pkmgr.install_package(f".\\sbin\\{command[0]}.pkg", ".\\sbin")
                continue
        except FileNotFoundError:
            pass
            continue

        # End dangerous space

        if command[0] == "exit":
            break
        elif command[0] == "echo":
            print(command[1])
        elif command[0] == "ls":
            for item in kernel.FileSystem.ListDir(".\\"):
                if kernel.IsDir(".\\" + item):
                    CPRINT(f"[{item}]", [0x0e, 0x00])
                else:
                    print(item)
        elif command[0] == "clear":
            os.system("cls")
        elif command[0] == "cd":
            try:
                kernel.FileSystem.ChangeDir(command[1])
            except OSError:
                CPRINT("Folder not found.", [0x0c, 0x00])
        elif command[0] == "mkdir":
            kernel.FileSystem.CreateDirectory(command[1])
        elif command[0].endswith(".kx"):
            try:
                application.execute_app(command[0])
            except FileNotFoundError:
                CPRINT("File not found.", [0x0c, 0x00])
        elif command[0].endswith(".kxa"):
            try:
                with open(command[0], "rb") as FH:
                    app = pickle.load(FH)
                appcode = marshal.loads(app["_text_"])
                exec(appcode["code"])
            except FileNotFoundError:
                CPRINT("File not found.", [0x0c, 0x00])
        elif command[0] == "mkdcd":
            kernel.FileSystem.CreateDirectory(command[1])
            kernel.FileSystem.ChangeDir(command[1])
        elif command[0] == "python":
            with open(command[1], "r") as FH:
                pc = FH.read()
            exec(pc)
        elif command[0] == "rm":
            try:
                if command[1].endswith(".py"):
                    CPRINT(f"[Delete]: {command[1]} is a system file, do you want to really delete it? (Y/n)",
                           [0x0e, 0x00])
                    CPRINT("It might make the system nonfunctional.", [0x04, 0x00])
                    while True:
                        yn = input("(Y/n)? ")
                        if yn.lower() == "y":
                            kernel.FileSystem.DeleteAny(command[1])
                            break
                        elif yn.lower() == "n":
                            break
                        CPRINT(f"Invalid choice: {yn}.", [0x0c, 0x00])
                elif command[1].endswith(".kx"):
                    CPRINT(f"[Delete]: {command[1]} is an application, do you want to really delete it? (Y/n)",
                           [0x0e, 0x00])
                    CPRINT("You will need to reinstall it later.", [0x04, 0x00])
                    while True:
                        yn = input("(Y/n)? ")
                        if yn.lower() == "y":
                            kernel.FileSystem.DeleteAny(command[1])
                            break
                        elif yn.lower() == "n":
                            break
                        CPRINT(f"Invalid choice: {yn}.", [0x0c, 0x00])
                else:
                    kernel.FileSystem.DeleteAny(command[1])
            except FileNotFoundError:
                CPRINT("File not found.", [0x0c, 0x00])
        elif command[0].endswith(".pkg"):
            try:
                pkmgr.install_package(command[0], command[1])
            except IndexError:
                CPRINT("Invalid number of arguments.", [0x0c, 0x00])
        elif command[0] == "spath":
            if command[1].lower() == "--add":
                SPATH.append(command[2])
                with open("path.sys", "wb") as FH:
                    marshal.dump(SPATH, FH)
            if command[1].lower() == "--list":
                CPRINT(f"{[(idx, obj) for idx, obj in enumerate(SPATH)]}; length {len(SPATH)}", [0x0e, 0x00])
            if command[1].lower() == "--remove":
                idx = 0
                try:
                    kernel.Types.ParseInt(command[2], idx)
                    SPATH.pop(idx)
                except ValueError:
                    CPRINT(f"Index {command[2]} of SPATH not found.", [0x0c, 0x00])
                with open("path.sys", "wb") as FH:
                    marshal.dump(SPATH, FH)
        elif command[0] == "refreshpath":
            with open("path.sys", 'rb') as FH:
                SPATH = marshal.load(FH)
        elif command[0] == "cp":
            if len(command) == 3:
                filecopysuccess = kernel.FileSystem.CopyFile(command[1], command[2])
                if not filecopysuccess:
                    CPRINT("Either one or another file does not exists.", [0x0c, 0x00])
            else:
                CPRINT("Invalid number of arguments.", [0x0c, 0x00])
        elif command[0] == "services":
            if command[1].lower() == "klog":
                if command[2] == "-delete" or command[2] == "--d":
                    for element in kernel.FileSystem.ListDir(".\\"):
                        if element.endswith(".log"):
                            #print(element)
                            kernel.FileSystem.DeleteAny(element)
        elif command[0] == "read":
            if len(command) == 2:
                rs = pathlib.Path(command[1]).exists()
                if not rs:
                    CPRINT("File not found.", [0x0c, 0x00])
                    continue
                with open(command[1]) as FH:
                    lines = FH.read()
                lines = lines.split("\n")
                for line in lines:
                    CPRINT(line, [0x0f, 0x00])
            else:
                CPRINT("Invalid number of arguments.", [0x0c, 0x00])
        else:
            CPRINT(f"Invalid application, package or command: {command[0]};\n"
                   f"Please verify the command, or if the app/package exists then retry.", [0x04, 0x00, True])
    except (IndexError, ModuleNotFoundError, FileNotFoundError) as e:
        if isinstance(e, ModuleNotFoundError):
            CPRINT(f"A kernel module was attempted to be loaded; without success.\n"
                   f"Module in question: '{e.name}'.", [0x0c, 0x00])
        elif isinstance(e, FileNotFoundError):
            CPRINT("File not found.", [0x0c, 0x00])
        else:
            CPRINT("Invalid number of arguments.", [0x0c, 0x00])
