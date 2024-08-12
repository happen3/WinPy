from klib.sharedlibs.user import User
from klib import kcrypto

class AuthToken:
    def __init__(self, user: User, permitted: bool):
        self.pm = permitted
        self.uid = kcrypto.Crypto.hash("sha256", user.password) + b"-" + user.name.encode()

    def getUID(self):
        return self.uid, "REJECT" if not self.pm else "ALLOW"


def CheckPermissions(action: str, filepath: str, user: User):
    if "*" in user.group.perms:
        return AuthToken(user, True).getUID()
    if f"ALLOW_{action.upper()}" in user.group.perms:
        return AuthToken(user, True).getUID()
    else:
        return AuthToken(user, False).getUID()
