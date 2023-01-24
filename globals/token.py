import json
import os
import globals.config

TOKEN_PATH = os.path.join(globals.config.APP_SETTINGS_DIR, ".token.json")

def check_data_dir_exists():
    """checks the data path exists if doesnt then dir will be created
    """
    if not os.path.exists(globals.config.APP_DATA_DIR):
        os.makedirs(globals.config.APP_DATA_DIR)

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