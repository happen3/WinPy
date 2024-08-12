import marshal
import pickle
import zipfile
from typing import Tuple


def generate_app(code: str, name: str = "test-app", desc: str = "Test Application", version: float = 1.00,
                 include: dict = None, appexeclvl: int = 0, permissions=None, filepath: str = ".\\app.kx"):
    if permissions is None:
        permissions = ["READ", "WRITE"]
    include = {"license": None} if include is None else include
    co_dat = compile(code, "<string>", "exec")
    serialized_co_dat = {
        "code": co_dat,
        "filename": "<string>",
        "mode": "exec"
    }
    appcode = marshal.dumps(serialized_co_dat)
    app = {
        "_text_": appcode,
        "_data_": {
            "name": name,
            "desc": desc,
            "version": version
        },
        "_manifest_": {
            "app_executionLevel": appexeclvl,
            "app_permissions": permissions
        },
        "_idat_": {
            "license": include["license"]
        }
    }

    with open(filepath, "wb") as FH:
        pickle.dump(app, FH)


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


def app_info(filepath: str):
    with open(filepath, "rb") as FH:
        app = pickle.load(FH)
    return app["_data_"], app["_idat_"], app["_manifest_"]


def generate_package(files: list[str], output_path: str):
    with zipfile.ZipFile(output_path, "w") as ZH:
        for item in files:
            ZH.write(item)


if __name__ == '__main__':
    generate_app("print('Hello, World!')")
    print(app_info("..\\sbin\\app.kx"))
