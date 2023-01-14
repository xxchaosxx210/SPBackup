import sqlite3
import os
import time

import spotify.debugging
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlist import Playlist

PLAYLIST_PATHNAME = "user_backups"
DATABASE_FILENAME = "playlists.db"
TEMP_DATABASE_FILENAME = ".current_playlists.db"
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
        await self.create_tables()
        return self.db_path
    
    async def create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            # setup the database
            cursor = conn.cursor()
            await self.create_backup_table(cursor)
            await self.create_playlist_table(cursor)
            await self.create_album_table(cursor)
            await self.create_artists_table(cursor)
            await self.create_track_table(cursor)
            conn.commit()

    async def create_backup_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Backups (
                        id INTEGER PRIMARY KEY,
                        name TEXT,
                        description TEXT,
                        date_added INTEGER);''')
    
    async def create_playlist_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            backup_id INTEGER,
            FOREIGN KEY (backup_id) REFERENCES Backups(id));
        ''')
    
    async def create_track_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Track (
            id INTEGER PRIMARY KEY,
            uri TEXT NOT NULL,
            name TEXT NOT NULL,
            playlist_id INTEGER,
            artists_id INTEGER,
            album_id INTEGER,
            FOREIGN KEY (playlist_id) REFERENCES Playlist(id),
            FOREIGN KEY (artists_id) REFERENCES Artists(id),
            FOREIGN KEY (album_id) REFERENCES Album(id)
        );
        ''')

    async def create_album_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Album(
            id INTEGER PRIMARY KEY,
            name TEXT
        );
        ''')

    async def create_artists_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Artists(
            id INTEGER PRIMARY KEY,
            name TEXT
        );
        ''')
    
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
    await pl.create_tables()
    # await pl.add_backup({
    #     "name": "CPM"
    # })

if __name__ == '__main__':
    import asyncio
    asyncio.run(_test())