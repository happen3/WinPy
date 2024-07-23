import marshal
import pickle
import zipfile


def generate_app(code: str, name: str = "test-app", desc: str = "Test Application", version: float = 1.00, include: dict = None, filepath: str = ".\\app.kx"):
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
        "_idat_": {
            "license": include["license"]
        }
    }

    with open(filepath, "wb") as FH:
        pickle.dump(app, FH)


def execute_app(filepath: str):
    with open(filepath, "rb") as FH:
        app = pickle.load(FH)
    appcode = marshal.loads(app["_text_"])
    exec(appcode["code"])


def app_info(filepath: str):
    with open(filepath, "rb") as FH:
        app = pickle.load(FH)
    return app["_data_"], app["_idat_"]


def generate_package(files: list[str], output_path: str):
    with zipfile.ZipFile(output_path, "w") as ZH:
        for item in files:
            ZH.write(item)


if __name__ == '__main__':
    generate_app("print('Hello, World!')")
    print(app_info("sbin/app.kx"))
