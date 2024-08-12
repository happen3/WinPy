import pickle
import marshal
import kernel
import klib.db
from klib import commandparser
from klib import application
from klib import pkmgr
from klib import kcrypto as kcrypto
from klib.sharedlibs.user import Dummy, User
import os
import sys
import pathlib
from klib import klog

CPRINT = kernel.stdio.cprint


def save(dictdb: dict, path: str):
    with open(path, "wb") as FH:
        pickle.dump(dictdb, FH)


def FALLBACK_CPRINT(text: str, attributes: list[bool | int]):
    fake_attributes = attributes
    print(text)


if not sys.stdout.isatty():
    print("This environnment does not supports colour!\nFallback to FALLBACK_CPRINT will be used.")
    CPRINT = FALLBACK_CPRINT

UserRegistry = []
klog.LoggedFile("Finished registering users").log()
idx: int = 0
klog.LoggedFile("Starting up command line!").log()
activeusername: None | str = None
users = []  # At least, if it fails, we'll end up with a defined user array instead of just nothing...
if not pathlib.Path(".\\users.db").exists():
    UserRegistry = [kernel.User("root", kernel.Administrator(), kernel.KERNEL_DEFAULT_PASSWORD.encode(), [])]
    CPRINT(
        "You are using the default password: '1234'!\nPlease change it the soonest time possible for security reasons."
        , [0x0c, 0x00, True])
    users = klib.db.Database("users")
    for i, user in enumerate(UserRegistry):
        users[i] = user
    # write
    users.save(".\\users.db")
else:
    with open(".\\users.db", "rb") as FH:
        UserRegistry: list | dict = pickle.load(FH)
        users = UserRegistry
    for DUser in UserRegistry["users"].values():
        #print(UserRegistry)
        DummyUser = kernel.User(DUser.name, Dummy(), kernel.KERNEL_DEFAULT_PASSWORD.encode(), [])
        DummyUser.salt = DUser.salt
        DummyUser.regenerate_password()
        if DUser.password == DummyUser.password:
            CPRINT(
                "You are using the default password: '1234'!\nPlease change it the sonnest time possible for security "
                "reasons."
                , [0x0c, 0x00, True])
if not pathlib.Path("path.sys").exists():
    SPATH = [".\\sbin\\"]
    with open("path.sys", "wb") as FH:
        marshal.dump(SPATH, FH)
else:
    with open("path.sys", 'rb') as FH:
        SPATH = marshal.load(FH)

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


def GetUserHandleOfActiveUserName(ActiveUserName: str) -> kernel.User | None:
    if isinstance(UserRegistry, list):
        return UserRegistry[0]
    for ruser in UserRegistry["users"].values():
        if ruser.name == ActiveUserName:
            #print(ruser)
            return ruser
    return None


def SetCurrentUserContext(newUser: kernel.User):
    global activeusername
    activeusername = newUser.name


def GetHookOfCurrentUser():
    userhandle = GetUserHandleOfActiveUserName(activeusername)
    return activeusername, userhandle


SetCurrentUserContext(GetUserHandleOfActiveUserName("root"))


def GetCurrentUser(ActiveUserName: str):
    UserHandle = GetUserHandleOfActiveUserName(ActiveUserName)
    if UserHandle == None:
        CPRINT("User does not exists or is invalid.", [0x0c, 0x00])
    return UserHandle


def execute_app(filepath: str, userPermissions: list[str], userGroupType: int = 0) -> tuple[str, str] | None:
    with open(filepath, "rb") as FH:
        app = pickle.load(FH)
    for perm in app["_manifest_"]["app_permissions"]:
        if "*" in userPermissions:
            break
        if perm not in userPermissions:
            return "REJECT", "Not enough permissions for user."
    if userGroupType < app["_manifest_"]["app_executionLevel"]:
        return "REJECT", "Group permission level does not permits execution of this app."
    appcode = marshal.loads(app["_text_"])
    exec(appcode["code"])


CPRINT("## WinPy kernel ##\r", [0x0e, 0x00])
print()
while __name__ == "__main__":

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
                UserHandle = GetUserHandleOfActiveUserName(activeusername)
                if UserHandle is None:
                    CPRINT("Current user does not exists or is invalid", [0x0c, 0x00])
                    continue
                success = application.execute_app(f".\\sbin\\{command[0]}.kx",
                                                  UserHandle.group.perms + UserHandle.addedperms,
                                                  UserHandle.group.grouptype)
                if isinstance(success, list) and success[0] == "REJECT":
                    CPRINT(f"Permission denied.\nReason: {success[1]}", [0x0c, 0x00])
                continue
            if pathlib.Path(f".\\sbin\\{command[0]}.kxa").exists():
                UserHandle = GetUserHandleOfActiveUserName(activeusername)
                if UserHandle is None:
                    CPRINT("Current user does not exists or is invalid", [0x0c, 0x00])
                    continue
                success = execute_app(f".\\sbin\\{command[0]}.kxa", UserHandle.group.perms + UserHandle.addedperms,
                                      UserHandle.group.grouptype)
                if isinstance(success, list) and success[0] == "REJECT":
                    CPRINT(f"Permission denied.\nReason: {success[1]}", [0x0c, 0x00])
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
        if command[0] == "getenv":
            if command[1] == "--List" or command[1] == "-l":
                CPRINT("Environment variables:", [0x06, 0x00])
                for k in os.environ:  # Subject to change
                    w = os.environ[k]  # Subject to change
                    CPRINT(f"{k} = {w}", [0x09, 0x00])
                continue
            CPRINT(f"{command[1]}: {os.environ.get(command[1], None)}", [0x06, 0x00])
        elif command[0] == "ginf":
            if command[1] in kernel.GROUPS:
                pass
            else:
                CPRINT("Group not found", [0x0c, 0x00])
                continue
            print(f"Group information for {command[1]}:")
            a = 0
            for group in kernel.GROUPSCLS:
                if command[1] == group[0]:
                    print(f"Group name  : {group[0]}")
                    print(f"Permissions : {group[1].perms}")
                    print(f"Group type  : {group[1].grouptype}")
                    a = 1
                    break
            if a == 0:
                CPRINT("Group not found", [0x0c, 0x00])
        elif command[0] == "swu":
            UserHandle = GetCurrentUser(command[1])
            if UserHandle is None: continue
            CPRINT("Please type the password of the target user (won't be echoed): ", [0x0e, 0x00])
            up = kernel.stdio.ReadLineNE()
            if kernel.usec.PasswordRead(up, UserHandle):
                SetCurrentUserContext(UserHandle)
                CPRINT("Switched user successfully", [0x09, 0x00])
            else:
                CPRINT(f"Invalid password for user {UserHandle.name}.", [0x0c, 0x00])
        elif command[0] == "user":
            if command[1] == "--New" or command[1] == "-c":
                NewUserName = command[2]
                NewUserPassword = command[3]
                NewUserGroup = command[4]
                found = 0
                for group in kernel.GROUPSCLS:
                    if NewUserGroup == group[0]:
                        NewUserGroup = group[1]
                        found = 1
                        break
                if found != 0:
                    CPRINT("Unknown group", [0x0c, 0x00])
                NewUser = User(NewUserName, NewUserGroup, NewUserPassword.encode(), [])
                users["users"][len(users["users"])] = NewUser
                save(users, ".\\users.db")
            elif command[1] == "--List" or command[1] == "-l":
                CPRINT("Users available:", [0x06, 0x00])
                for user in users["users"]:
                    if activeusername == users["users"][user].name:
                        if users["users"][user].name == "root":
                            CPRINT(users["users"][user].name + " [Logged in]", [0x0c, 0x00])
                        else:
                            print(users["users"][user].name + " [Logged in]")
                    else:
                        print(users["users"][user].name)
        elif command[0] == "passwd":
            if len(command) == 2:
                with open(".\\users.db", "rb") as FH:
                    UserRegistry: list | dict = pickle.load(FH)
                    users = UserRegistry
                UserHandle = GetHookOfCurrentUser()
                CPRINT("Please type in your current password (won't be echoed): ", [0x0e, 0x00])
                np = kernel.stdio.ReadLineNE()
                Handle = GetHookOfCurrentUser()
                if Handle[0] is None:
                    CPRINT("The current user or does not exist or is invalid.", [0x0c, 0x00])
                    continue
                if Handle[1] is None:
                    CPRINT("The current user or does not exist or is invalid.", [0x0c, 0x00])
                    continue
                if kernel.usec.PasswordRead(np, Handle[1]):
                    CPRINT("Password set.", [0x0e, 0x00])
                    for obj in users["users"]:
                        tuser = users["users"][obj]
                        if tuser.name == Handle[0]:
                            HashedPass = kcrypto.Crypto.hash("sha256", command[1].encode())
                            tuser.salt = kcrypto.Crypto.generate_salt(16)
                            tuser.password = kcrypto.Crypto.salt(tuser.salt, HashedPass)
                            break
                    save(users, ".\\users.db")  # Would be funny to not save at that point, no?
                else:
                    CPRINT("Password is invalid.", [0x0c, 0x00])
            else:
                print("Usage: passwd [new_password]")
        elif command[0] == "echo":
            print(command[1])
        elif command[0] == "ls":
            ShowHidden = None
            if len(command) == 2:
                if command[1] == "--Force" or command[1] == "-f":
                    ShowHidden = True
                else:
                    ShowHidden = False
            else:
                ShowHidden = False
            for item in kernel.FileSystem.ListDir(".\\"):
                if kernel.IsDir(".\\" + item):
                    if ShowHidden and item.startswith("."):
                        CPRINT(f"[{item}]", [0x0e, 0x00])
                    if not item.startswith("."):
                        CPRINT(f"[{item}]", [0x0e, 0x00])
            for item in kernel.FileSystem.ListDir(".\\"):
                if not kernel.IsDir(".\\" + item):
                    if item.endswith(".kx") or item.endswith(".kxa"):
                        CPRINT(f"{item}", [0x09, 0x00])
                    elif item.endswith(".py"):
                        CPRINT(f"{item}", [0x0a, 0x00])
            for item in kernel.FileSystem.ListDir(".\\"):
                if not kernel.IsDir(item):
                    if not item.endswith(".kx") and not item.endswith(".kxa") and not item.endswith(".py"):
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
                UserHandle = GetUserHandleOfActiveUserName(activeusername)
                if UserHandle is None:
                    CPRINT("Current user does not exists or is invalid", [0x0c, 0x00])
                    continue
                success = application.execute_app(f".\\sbin\\{command[0]}.kxa",
                                                  UserHandle.group.perms + UserHandle.addedperms,
                                                  UserHandle.group.grouptype)
                if isinstance(success, list) and success[0] == "REJECT":
                    CPRINT(f"Permission denied.\nReason: {success[1]}", [0x0c, 0x00])
                continue
            except FileNotFoundError:
                CPRINT("File not found.", [0x0c, 0x00])
        elif command[0].endswith(".kxa"):
            try:
                UserHandle = GetUserHandleOfActiveUserName(activeusername)
                if UserHandle is None:
                    CPRINT("Current user does not exists or is invalid", [0x0c, 0x00])
                    continue
                success = execute_app(f".\\sbin\\{command[0]}.kxa", UserHandle.group.perms + UserHandle.addedperms,
                                      UserHandle.group.grouptype)
                if isinstance(success, list) and success[0] == "REJECT":
                    CPRINT(f"Permission denied.\nReason: {success[1]}", [0x0c, 0x00])
                continue
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
                    if "DELETE" in GetCurrentUser(activeusername).group.perms or "*" in GetCurrentUser(activeusername).group.perms or GetCurrentUser(
                            activeusername) in GetCurrentUser(activeusername).addedperms:
                        pass
                    else:
                        CPRINT("Permission denied.", [0x0c, 0x00])
                        continue
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
                    if "DELETE" in GetCurrentUser(activeusername).group.perms or "*" in GetCurrentUser(activeusername).group.perms or GetCurrentUser(
                            activeusername) in GetCurrentUser(activeusername).addedperms:
                        pass
                    else:
                        CPRINT("Permission denied.", [0x0c, 0x00])
                        continue
                    CPRINT(f"[Delete]: {command[1]} is an application, do you want to really delete it? (Y/n)",
                           [0x0e, 0x00])
                    CPRINT('You will need to reinstall it later.', [0x04, 0x00])
                    while True:
                        yn = input('(Y/n)? ')
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
        elif command[0] == "cwu":
            if len(command) == 2:
                if command[1] == "-i":
                    UserHandle = GetUserHandleOfActiveUserName(activeusername)
                    if UserHandle == None:
                        CPRINT("User does not exists or is invalid.", [0x0c, 0x00])
                    CPRINT(f"Information for user {activeusername}:", [0x09, 0x00])
                    print(f"Group: {UserHandle.group.groupname}")
                    print(f"Created on: {UserHandle.created}")
                    continue
            print(activeusername)
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
