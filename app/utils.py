import json
import os

def save(token):
    with open("token.json", "w") as fp:
        fp.write(json.dumps({
            "token": token
        }))

def load():
    try:
        with open("token.json", "r") as fp:
            return json.loads(fp.read())
    except FileNotFoundError:
        return {"token": None}

def remove():
    if os.path.exists("token.json"):
        save(None)