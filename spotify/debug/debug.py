import os
import logging
import json

DEBUG = False

DEBUG_LOGGER = "debug"
DEBUG_LOG_FILENAME = "debug.log"

DEBUG_PATH = os.path.dirname(__file__)
DATA_PATH = os.path.join(DEBUG_PATH, "data")


def send_to_log(message: str, level: str):
    if not DEBUG:
        return
    _Log = logging.getLogger(DEBUG_LOGGER)
    if level == "info":
        _Log.info(message)
    elif level == "debug":
        _Log.debug(message)
    elif level == "warning":
        _Log.warning(message)
    else:
        _Log.error(message)


def intialize_filelogger(logger_name: str = DEBUG_LOGGER, filename: str = DEBUG_LOG_FILENAME) -> bool:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return True

def initialize():
    intialize_filelogger()
    if os.path.exists(DATA_PATH):
        return
    try:
        os.mkdir(DATA_PATH)
        send_to_log(f"Data directory for json output has been created in path: {DATA_PATH}", "info")
    except OSError as e:
        send_to_log(f'Error creating debug/data directory. {e.__str__()}', "error")
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
            send_to_log(f"Data has been saved to {pathname}", "info")
    except Exception as err:
        send_to_log(f"Error in writing to {pathname}. {err.__str__()}", "error")
        result = False
    finally:
        return result

