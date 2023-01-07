import json
import os

TOKEN_FILENAME = ".token.json"

def save(token):
    with open(TOKEN_FILENAME, "w") as fp:
        fp.write(json.dumps({
            "token": token
        }))

def load():
    try:
        with open(TOKEN_FILENAME, "r") as fp:
            return json.loads(fp.read())
    except FileNotFoundError:
        return {"token": None}

def remove():
    if os.path.exists(TOKEN_FILENAME):
        save(None)