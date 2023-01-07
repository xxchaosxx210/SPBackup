import os
import logging
import json

DEBUG = False

_Log = logging.getLogger()

DEBUG_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(DEBUG_PATH, "data")


def initialize_paths():
    if os.path.exists(DATA_PATH):
        return
    try:
        os.mkdir(DATA_PATH)
        _Log.info(f"Data directory for json output has been created in path: {DATA_PATH}")
    except OSError as e:
        _Log.error(f'Error creating debug/data directory. {e.__str__()}')
    finally:
        return

def save(filename: str, data: object) -> bool:
    if not DEBUG:
        return False
    result = True
    try:
        pathname = os.path.join(DATA_PATH, filename)
        with open(pathname, "w") as fp:
            fp.write(json.dumps(data))
            _Log.info(f"Data has been saved to {pathname}")
    except Exception as err:
        _Log.error(f"Error in writing to {pathname}. {err.__str__()}")
        result = False
    finally:
        return result

