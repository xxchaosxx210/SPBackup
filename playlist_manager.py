import sqlite3
import os
import logging

import spotify.debugging
from spotify.validators.user import User as SpotifyUser

PLAYLIST_PATHNAME = "user_backups"
DATABASE_FILENAME = "playlists.db"
PLAYLIST_DIR: str = ""


class PlaylistManager:

    def __init__(self) -> None:
        global PLAYLIST_DIR
        self.user: SpotifyUser = None
        self.db_path: str = ""
        PLAYLIST_DIR = os.path.join(
            spotify.debugging.APP_SETTINGS_DIR, PLAYLIST_PATHNAME)
    
    async def create_backup_directory(self, user: SpotifyUser) -> str:
        """creates a folder named after the UserID if doesnt exist
        then it creates a sqlite database if one doesnt exist. Then it
        adds a table named user with the user details

        Args:
            path (str): the exact path of the apps settings

        Returns:
            str: returns the pathname to where the database was created
        """
        user_path = os.path.join(PLAYLIST_DIR, f'{user.id}')
        try:
            os.makedirs(user_path, exist_ok=False)
            spotify.debugging.file_log(f"Could not find playlist user path creating a new one... {user_path}", "info")
        except OSError as err:
            spotify.debugging.file_log(f"Playlist Backup User Path already exists: {user_path}", "info")
        self.db_path = os.path.join(user_path, DATABASE_FILENAME)