import pickle
from contextlib import contextmanager

import klib.db
from klib import kregistry
import marshal


@contextmanager
def ContinuousLogWriter(origin_time: str):
    try:
        with open(origin_time, "a") as FH:
            yield FH
    except OSError as e:
        print(f"Error opening file: {e}")


def fprintf(data, fh):
    try:
        fh.write(data)
    except AttributeError:
        print("Invalid file handler provided")


@contextmanager
def RegistryWriter(registry_index: str):
    try:
        with open(registry_index, "w+") as FH:
            yield FH
    except OSError as e:
        print(f"Error opening file: {e}")


def WriteRegistry(registry: kregistry.Registry, fh):
    try:
        fh.write(str(registry()))
    except AttributeError:
        print("Invalid file handler provided")


@contextmanager
def DatabaseWriter(database_location: str):
    try:
        with open(database_location, "wb") as FH:
            yield FH
    except OSError as e:
        print(f"Error opening file: {e}")


def WriteDB(database: dict, fh):
    try:
        pickle.dump(database, fh)
    except AttributeError:
        print("The provided file handler is invalid.")