import sqlite3
import os
import logging
import time

import spotify.debugging
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlist import Playlist

PLAYLIST_PATHNAME = "user_backups"
DATABASE_FILENAME = "playlists.db"
PLAYLIST_DIR: str = ""


"""
@dataclass
class Backups:
    id: int
    name: str
    description: str
    date_added: int

@dataclass
Playlist:
    id: int
    backups_id: int     #foreign key
    name: str
    description: str

@dataclass
Track
    id: int
    playlist_id: int    #foreign key
    artists_id: int     #foreign key
    album_id: int       #foreign key
    uri: str
    name: str

@dataclass
Artists:
    id: int
    name: str

@dataclass
Album:
    id: int
    name: str
"""

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
            # path already exists
            pass
        self.db_path = os.path.join(user_path, DATABASE_FILENAME)
        with sqlite3.connect(self.db_path) as conn:
            # setup the database
            cursor = conn.cursor()
            await self.create_backup_table(cursor)
            """
            import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Backups table
cursor.execute('''
    CREATE TABLE Backups (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        date_added INTEGER
    )
''')

# Playlist table
cursor.execute('''
    CREATE TABLE Playlist (
        id INTEGER PRIMARY KEY,
        backups_id INTEGER,
        FOREIGN KEY (backups_id) REFERENCES Backups(id),
        name TEXT,
        description TEXT
    )
''')

# Track table
cursor.execute('''
    CREATE TABLE Track (
        id INTEGER PRIMARY KEY,
        playlist_id INTEGER,
        FOREIGN KEY (playlist_id) REFERENCES Playlist(id),
        artists_id INTEGER,
        FOREIGN KEY (artists_id) REFERENCES Artists(id),
        album_id INTEGER,
        FOREIGN KEY (album_id) REFERENCES Album(id),
        uri TEXT,
        name TEXT
    )
''')

# Artists table
cursor.execute('''
    CREATE TABLE Artists (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

# Album table
cursor.execute('''
    CREATE TABLE Album (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

conn.commit()
conn.close()

            """
            conn.commit()
        return self.db_path

    async def create_backup_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Backups (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        description TEXT,
                        date_added INTEGER);''')
    
    async def add_backup(self, backup: dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
            INSERT INTO backups (name, id, date_added)
            VALUES(?, ?, ?)''', (backup["name"], 1, time.time()))

async def _test():
    from spotify.validators.user import ExternalUrls, Followers, Image
    user: SpotifyUser = SpotifyUser(
        display_name="CPM",
        external_urls=ExternalUrls(spotify=""),
        followers=Followers(href="",  total=4),
        href="https://testsomewhere.com",
        id="CPM",
        images=[Image(height=0, url="", width=1)],
        type="",
        uri="https://somewhere/spotify.com"
    )
    pl: PlaylistManager = PlaylistManager()
    await pl.create_backup_directory(user=user)
    # await pl.add_backup({
    #     "name": "CPM"
    # })

if __name__ == '__main__':
    import asyncio
    asyncio.run(_test())