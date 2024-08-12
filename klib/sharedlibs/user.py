import math
from time import time

import klib.kcrypto


class Group:
    def __init__(self, permissionlevel, permissions, name):
        self.pl = permissionlevel
        self.perms = permissions
        self.groupname = name
        self.grouptype = 1

    def is_allowed(self, action, minpermissionlevel):
        return True if action in self.perms and self.pl >= minpermissionlevel else False


class Administrator(Group):
    def __init__(self):
        super().__init__(120, ["*", "administrator"], "Administrator")
        self.grouptype = 2


class Dummy(Group):
    def __init__(self):
        super().__init__(-20, ["none"], "Dummy Group")
        self.grouptype = -1


class UserGroup(Group):
    def __init__(self):
        super().__init__(0, ["READ", "WRITE", "ACCESS", "DELETE_NS"], "Users")
        self.grouptype = 0


class User:
    def __init__(self, username, group, password, aperms):
        self.name: str = username
        self.group: Group = group
        self.created: int = math.floor(time())
        self.salt: bytes = klib.kcrypto.Crypto.generate_salt(16)
        self.password: bytes = klib.kcrypto.Crypto.salt(self.salt, klib.kcrypto.Crypto.hash("sha256", password))
        self.addedperms: list[str] = aperms

    def regenerate_password(self):
        self.password: bytes = klib.kcrypto.Crypto.salt(self.salt, klib.kcrypto.Crypto.hash("sha256", self.password))
