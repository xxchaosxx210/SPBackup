"""
playlist_manager.py - handles the users playlists and backs up and restores them using sqlite3
and json
"""

import sqlite3
import os
import asyncio
from datetime import datetime
from enum import (
    Enum,
    auto as enum_auto
)
from typing import Callable, Dict, Union

import spotify.debugging
import spotify.net
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlist import Playlist
from spotify.validators.playlists import Playlists

PLAYLIST_PATHNAME = "user_backups"
# backed up playlists
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

MAX_PLAYLISTS_CONNECT = 5
MAX_TRACKS_CONNECT = 5


class BackupEventType(Enum):
    """for our function callback

    Args:
        Enum (int): ID of the event that has happened
    """

    BACKUP_SUCCESS = enum_auto()
    BACKUP_ERROR = enum_auto()
    BACKUP_PLAYLIST_ADDED = enum_auto()


class BackupSQlite:

    """Backup Context Manager for connecting to the database
    """

    def __init__(self, filepath) -> None:
        self.filepath = filepath
    
    def __enter__(self, *args, **kwargs) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.filepath)
        return self.conn.cursor()
    
    def __exit__(self, *args, **kwargs):
        self.conn.commit()
        self.conn.close()


BACKUP_CALLBACK_TYPE = Callable[[BackupEventType, Union[Dict, str]], None]


class PlaylistManager:

    running_task: asyncio.Task = None

    def __init__(self) -> None:
        # settings ans setting up the database tables
        global PLAYLIST_DIR
        self.user: SpotifyUser = None
        self.db_path: str = ""
        PLAYLIST_DIR = os.path.join(
            spotify.debugging.APP_SETTINGS_DIR, PLAYLIST_PATHNAME)


    async def playlists(self, token: str, limit: int):
        """generator function for retrieving playlists and yielding at one playlist per time

        Args:
            token (str): the spotify access token
            limit (int): the maximum amount of playlists per request

        Yields:
            Playlist: the spotify.validators.playlists.Playlist object
        """
        offset = 0
        playlists = await spotify.net.get_playlists(
            token,
            offset=offset,
            limit=limit)
        # playlists_items = playlists.items
        total_playlists = playlists.total
        while total_playlists > 0:
            for playlist in playlists.items:
                yield playlist
            offset += limit
            playlists = await spotify.net.get_playlists(
                token, offset=offset, limit=limit)
            total_playlists -= len(playlists.items)

    async def backup_playlists(self,
                               callback: BACKUP_CALLBACK_TYPE,
                               token: str,
                               backup_name: str,
                               backup_description: str,
                               limit: int = 50):
        """where the backup begins and the main coroutine task handler

        Args:
            callback (BACKUP_CALLBACK_TYPE): the callback to send data back to
            token (str): the authenticating spotify token
            backup_name (str): the name of the backup to be added to the database
            backup_description (str): the description of the backup entry
            limit (int, optional): maximum number of playlists in every HTTP response. Defaults to 50.
        """
        # create a backup entry to the sqlite3 database
        await self.add_backup(backup_name, backup_description)
        # temporary storage for holding tasks
        self.tasks = []
        async for playlist in self.playlists(token, limit):
            callback(BackupEventType.BACKUP_PLAYLIST_ADDED,
                     {"playlist": playlist})
            self.tasks.append(
                self.insert_playlist_db(playlist))
            if len(self.tasks) >= MAX_PLAYLISTS_CONNECT:
                # gather will call create_task automatically
                await asyncio.gather(*self.tasks)
                self.tasks = []
        if self.tasks:
            await asyncio.gather(*self.tasks)

        callback(BackupEventType.BACKUP_SUCCESS, {})

    async def add_backup(self, name: str, description: str) -> int:
        """adds a backup entry to the database file

        Args:
            name (str): Name of the backup
            description (str): brief description of the backup. Can be empty

        Returns:
            int: the Backup Primary Key ID
        """
        date_added = datetime.now()
        with BackupSQlite(self.db_path) as cursor:
            cursor.execute('''
            INSERT INTO Backups (name, description, date_added)
            VALUES(?, ?, ?)''', (name, description, date_added))
            cursor.execute("SELECT id from Backups WHERE date_added = ?", (date_added,))
            result: any = cursor.fetchone()[0]
            return result

    async def insert_playlist_db(self, playlist: Playlist):
        """insert the playlist into the database file

        Args:
            playlist (Playlist): the playlist object to add
        """
        # print(playlist.name)
        pass

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
            spotify.debugging.file_log(
                f"Could not find playlist user path creating a new one... {user_path}", "info")
        except OSError:
            # path already exists
            pass
        finally:
            self.db_path = os.path.join(user_path, DATABASE_FILENAME)
            await self.create_tables()
            return self.db_path

    async def create_tables(self):
        with BackupSQlite(self.db_path) as cursor:
            # setup the database
            await self.create_backup_table(cursor)
            await self.create_playlist_table(cursor)
            await self.create_album_table(cursor)
            await self.create_artists_table(cursor)
            await self.create_track_table(cursor)

    async def create_backup_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Backups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        description TEXT,
                        date_added DATETIME NOT NULL);''')

    async def create_playlist_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Playlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            backup_id INTEGER,
            FOREIGN KEY (backup_id) REFERENCES Backups(id));
        ''')

    async def create_track_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Track (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        ''')

    async def create_artists_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Artists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        ''')


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

if __name__ == '__main__':
    import asyncio
    asyncio.run(_test())
