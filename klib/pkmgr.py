import marshal
import os.path
import shutil
import zipfile
from klib import kcolor
from klib import application
from klib.filewriter import RegistryWriter, WriteRegistry
from klib import kregistry
import ast


def __interface__CPRINT(data: str, attributes: list[int | bool]):
    kcolor.cprint(data, *attributes)


CPRINT = __interface__CPRINT
interface__CPRINT = CPRINT


def install_package(filename: str, location: str):
    with zipfile.ZipFile(filename, "r") as ZH:
        CPRINT(f"[Package Installer] Installing package {filename[:-3]}...", [0x0a, 0x00])
        ZH.extractall(location)
    CPRINT("[Package Installer] Executing install script...", [0x0a, 0x00])
    application.execute_app(f"{location}\\install\\install.kx")
    CPRINT("[Package Installer] Cleaning up...", [0x0a, 0x00])
    shutil.rmtree(f"{location}\\install\\")
    CPRINT("[Package Installer] Adding package to pkgreg...", [0x0a, 0x00])
    with open("..\\pkreg.reg", "r") as FH:
        try:
            reg = ast.literal_eval(FH.read())
        except SyntaxError:
            reg = {}

    def merge_dicts(d1, d2):
        for key, value in d2.items():
            if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                merge_dicts(d1[key], value)
            else:
                d1[key] = value

    print(reg)
    RG = kregistry.Registry()
    nrg = {filename[:-4]: {filename[:-4] + ".name": filename[:-4], filename[:-4] + ".size": os.path.getsize(filename)}}
    print(reg)
    merge_dicts(reg, nrg)
    RG.set(reg)
    print(RG())
    with RegistryWriter("..\\pkreg.reg") as FH:
        WriteRegistry(RG, FH)


if __name__ == '__main__':
    install_package("..\\osk.pkg", ".\\testd")
