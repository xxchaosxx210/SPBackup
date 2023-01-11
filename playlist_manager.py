import sqlite3
import os
from spotify.validators.user import User as SpotifyUser

DATABASE_FILENAME = "playlists.db"


def create_user_table(conn: sqlite3.Connection):
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (ID TEXT PRIMARY KEY NOT NULL,
                    DISPLAY_NAME TEXT NOT NULL,
                    SPOTIFY_URL TEXT NOT NULL,
                    FOLLOWERS_HREF TEXT,
                    FOLLOWERS_TOTAL INTEGER,
                    HREF TEXT NOT NULL,
                    IMAGE_HEIGHT INTEGER,
                    IMAGE_WIDTH INTEGER,
                    IMAGE_URL TEXT,
                    TYPE TEXT NOT NULL,
                    URI TEXT NOT NULL);''')
    conn.commit()

def insert_user(conn: sqlite3.Connection, user: SpotifyUser):
    conn.execute(
        "INSERT INTO users (ID, DISPLAY_NAME, SPOTIFY_URL, FOLLOWERS_HREF, FOLLOWERS_TOTAL, HREF, IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_URL, TYPE, URI) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
        (user.id, user.display_name, user.external_urls.spotify, user.followers.href, user.followers.total, user.href, user.images[0].height, user.images[0].width, user.images[0].url, user.type, user.uri))
    conn.commit()


class PlaylistManager:

    def __init__(self, settings_path: str) -> None:
        self.user: SpotifyUser = None
        self.db_path: str = ""
        self.__settings_path = settings_path
    
    def create_user(self, user: SpotifyUser) -> str:
        """creates a folder named after the UserID if doesnt exist
        then it creates a sqlite database if one doesnt exist. Then it
        adds a table named user with the user details

        Args:
            path (str): the exact path of the apps settings

        Returns:
            str: returns the pathname to where the database was created
        """
        user_path = os.path.join(self.__settings_path, f'{user.id}')
        os.makedirs(user_path, exist_ok=True)
        self.db_path = os.path.join(user_path, DATABASE_FILENAME)
        with sqlite3.connect(self.db_path) as conn:
            create_user_table(conn)
            insert_user(conn, user)
        return self.db_path