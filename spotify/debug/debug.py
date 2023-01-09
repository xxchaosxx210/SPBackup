import os
import logging
import json

DEBUG = False

# USER_DIR = os.path.expanduser("~")
APP_DATA_DIR = os.environ["ALLUSERSPROFILE"]
# Change this to whatever your app name is called
APP_NAME = "SPBackup"
APP_SETTINGS_DIR = os.path.join(APP_DATA_DIR, APP_NAME)
DEBUG_DIR = os.path.join(APP_SETTINGS_DIR, "debug")
DEBUG_DATA_DIR = os.path.join(DEBUG_DIR, "data")

DEBUG_LOGGER_NAME = "debug"
DEBUG_LOG_PATH = os.path.join(DEBUG_DIR, "debug.log")


def file_log(message: str, level: str):
    """logs message to debug.log in parent directory

    Args:
        message (str): the message to display in log file
        level (str): either "info"|"debug"|"warning"|"error"
    """
    if not DEBUG:
        return
    _Log = logging.getLogger(DEBUG_LOGGER_NAME)
    if level == "info":
        _Log.info(message)
    elif level == "debug":
        _Log.debug(message)
    elif level == "warning":
        _Log.warning(message)
    else:
        _Log.error(message)


def intialize_filelogger(logger_name: str = DEBUG_LOGGER_NAME, log_path: str = DEBUG_LOG_PATH):
    """this function is called within the intialize function but can be called seperatley

    Args:
        logger_name (str, optional): _description_. Defaults to DEBUG_LOGGER_NAME.
        filename (str, optional): _description_. Defaults to DEBUG_LOG_FILENAME.

    Returns:
        None
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    # check the debug direcrory exists
    # if not os.path.exists(log_path):
    #     os.makedirs(log_path)
    fh = logging.FileHandler(log_path)
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def initialize():
    """ call this function at the start of your app. Sets the file logger and creates a data path for storing json files retrieved from the spotify API
    """
    try:
        os.makedirs(DEBUG_DIR)
        intialize_filelogger()
    except OSError as err:
        print(f"Error creating {DEBUG_DIR} directory. Reason: {err.__str__()}")

    if os.path.exists(DEBUG_DATA_DIR):
        return
    try:
        os.makedirs(DEBUG_DATA_DIR)
        file_log(f"Data directory for json output has been created in path: {DEBUG_DATA_DIR}", "info")
    except OSError as e:
        file_log(f'Error creating debug/data directory. {e.__str__()}', "error")
    finally: 
        return


def save(filename: str, data: object) -> bool:
    """saves an object in the format of json string

    Args:
        filename (str): the filename to save to ./data/ path
        data (object): _description_

    Returns:
        bool: returns true if file was saved
    """
    if not DEBUG:
        return False
    result = True
    try:
        pathname = os.path.join(DEBUG_DATA_DIR, filename)
        with open(pathname, "w") as fp:
            fp.write(json.dumps(data))
            file_log(f"Data has been saved to {pathname}", "info")
    except Exception as err:
        file_log(f"Error in writing to {pathname}. {err.__str__()}", "error")
        result = False
    finally:
        return result

