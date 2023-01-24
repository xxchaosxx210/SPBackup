import os

# Global App data

APP_NAME = "SPBackup"
APP_VERSION = 1.0
APP_AUTHOR = "Paul Millar"

# Our Application Ids for the Spotify OAuth keep hidden!!!!
CLIENT_ID = "615b6e76033644d5b4cb68b7e11cbeb4"
CLIENT_SECRET = "88130c005e2041e98f1529e5f7aaf6e3"

APP_DATA_DIR = os.environ["ALLUSERSPROFILE"]
# Change this to whatever your app name is called
APP_NAME = "SPBackup"
APP_SETTINGS_DIR = os.path.join(APP_DATA_DIR, APP_NAME)

# backed up pathnames
USER_DATABASE_FILENAME = "backups.db"
USERS_FULL_PATHNAME = os.path.join(APP_SETTINGS_DIR, "users")

def create_data_path():
    from globals.logger import console
    console(f'Checking for {APP_SETTINGS_DIR}')
    try:
        os.makedirs(APP_SETTINGS_DIR)
        console(f'{APP_SETTINGS_DIR} has been created')
    except OSError:
        console(f"{APP_SETTINGS_DIR} already exists")

def create_users_path():
    from globals.logger import console
    console(f'Checking for {USERS_FULL_PATHNAME}')
    try:
        os.makedirs(USERS_FULL_PATHNAME)
        console(f'{USERS_FULL_PATHNAME} has been created')
    except OSError:
        console(f"{USERS_FULL_PATHNAME} already exists")