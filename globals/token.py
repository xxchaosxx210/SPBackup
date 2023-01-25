import json
import os
import globals.config
import logging

TOKEN_PATH = os.path.join(globals.config.APP_SETTINGS_DIR, ".token.json")

_Log = logging.getLogger()


def check_data_dir_exists():
    """checks the data path exists if doesnt then dir will be created
    """
    try:
        os.makedirs(globals.config.APP_DATA_DIR)
    except Exception as err:
        if isinstance(err, FileExistsError):
            return
        _Log.error(err.__str__())


def save(token: str, path: str = TOKEN_PATH):
    check_data_dir_exists()
    with open(path, "w") as fp:
        fp.write(json.dumps({"token": token}))


def load(path: str = TOKEN_PATH):
    check_data_dir_exists()
    try:
        with open(path, "r") as fp:
            return json.loads(fp.read())
    except FileNotFoundError:
        return {"token": None}


def remove(path: str = TOKEN_PATH):
    check_data_dir_exists()
    if os.path.exists(path):
        save(None)
