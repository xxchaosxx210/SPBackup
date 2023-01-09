import json
import os

APP_NAME = "SPBackup"
APP_VERSION = 1.0
APP_AUTHOR = "Paul Millar"

_USER_DIR = os.path.expanduser("~")
APP_DATA_DIR = os.path.join(_USER_DIR, APP_NAME)

TOKEN_PATH = os.path.join(APP_DATA_DIR, ".token.json")

def save(token: str, path: str = TOKEN_PATH):
    with open(path, "w") as fp:
        fp.write(json.dumps({
            "token": token
        }))

def load(path: str = TOKEN_PATH):
    try:
        with open(path, "r") as fp:
            return json.loads(fp.read())
    except FileNotFoundError:
        return {"token": None}

def remove(path: str = TOKEN_PATH):
    if os.path.exists(path):
        save(None)