import json
import os

TOKEN_FILENAME = "token.json"

def save(token: str):
    with open(TOKEN_FILENAME, "w") as fp:
        fp.write(json.dumps({
            "token": token
        }))

def load() -> dict:
    """loads the token object from the TOKEN_FILENAME

    Returns:
        dict: if token exists then there will be a token value. If no token then the token property
        will be null
    """
    try:
        with open(TOKEN_FILENAME, "r") as fp:
            return json.loads(fp.read())
    except FileNotFoundError:
        return {"token": None}

def remove():
    """checks TOKEN_FILENAMER exists and saves the token as null
    Note: doesnt delete the file TOKEN_FILENAME
    """
    if os.path.exists(TOKEN_FILENAME):
        save(None)