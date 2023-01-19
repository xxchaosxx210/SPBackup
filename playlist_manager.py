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
from types import AsyncGeneratorType

import spotify.debugging
import spotify.net
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlist import Playlist
from spotify.validators.playlists import Item as PlaylistItem
from spotify.validators.playlists import Playlists
from spotify.validators.tracks import Item as TrackItem

import globals.logger


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


def retry_on_exception(max_retries: int, error_handler: Callable[[str], None] = None):
    """decorator for handling network exceptions and retries

    Args:
        max_retries (int): _description_
        error_handler (Callable[[str],None], optional): _description_. Defaults to None.
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            function_instance = func(*args, **kwargs)
            # check if the function is the generator function
            if isinstance(function_instance, AsyncGeneratorType):
                async def _wrapper():
                    """this is the internal async function wrapper

                    Raises:
                        err: general exception

                    Yields:
                        any: value (playlist|track)
                    """
                    for i in range(max_retries):
                        try:
                            async for value in function_instance:
                                yield value
                        except Exception as err:
                            if i < max_retries-1:
                                globals.logger.console(
                                    f"Connection error (Reason: {err.__str__()}. Retrying...")
                                continue
                            if error_handler:
                                error_handler(err)
                            else:
                                raise err
            else:
                # standard async function just call and wait and return
                async def _wrapper():
                    return await func(*args, **kwargs)
            return _wrapper()
        return wrapper
    return decorator


class BackupEventType(Enum):
    """for our function callback

    Args:
        Enum (int): ID of the event that has happened
    """

    BACKUP_SUCCESS = enum_auto()
    BACKUP_ERROR = enum_auto()
    BACKUP_PLAYLIST_ADDED = enum_auto()
    BACKUP_PLAYLIST_STARTED = enum_auto()
    BACKUP_PLAYLIST_SUCCESS = enum_auto()
    BACKUP_PLAYLIST_ERROR = enum_auto()
    BACKUP_TRACKS_STARTED = enum_auto()
    BACKUP_TRACKS_SUCCESS = enum_auto()
    BACKUP_TRACKS_ERROR = enum_auto()
    BACKUP_TRACKS_ADDED = enum_auto()


class BackupSQlite:

    """Backup Context Manager for connecting to the database
    """

    def __init__(self, filepath) -> None:
        self.filepath = filepath

    def __enter__(self, *args, **kwargs) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.filepath)
        return self.conn.cursor()

    def __exit__(self, type: Exception, value: any, exception: object):
        if type:
            message = f'Error handling SQlite IO: {type}, {value}, {exception}'
            globals.logger.console(message, "error")
        self.conn.commit()
        self.conn.close()
        return True


BACKUP_CALLBACK_TYPE = Callable[[BackupEventType, Union[Dict, str]], None]


def on_error_handler(err: Exception):
    globals.logger.console(f"Failed to connect. Reason: {err.__str__()}")


class PlaylistManager:

    running_task: asyncio.Task = None

    def __init__(self) -> None:
        # settings ans setting up the database tables
        global PLAYLIST_DIR
        self.user: SpotifyUser = None
        self.db_path: str = ""
        PLAYLIST_DIR = os.path.join(
            spotify.debugging.APP_SETTINGS_DIR, PLAYLIST_PATHNAME)
        self.app_callback: BACKUP_CALLBACK_TYPE = None

    # @retry_on_exception(max_retries=3, error_handler=on_error_handler)
    async def _tracks(self, token: str, playlist_id: int, limit: int):
        offset = 0
        tracks = await spotify.net.get_playlist_tracks(
            access_token=token, playlist_id=playlist_id, offset=offset, limit=limit)
        track_counter = tracks.total
        total_tracks = tracks.total
        while track_counter > 0:
            for track in tracks.items:
                yield track
            offset += limit
            if offset > total_tracks:
                break
            # need to fix the bug this function is not correct
            tracks = await spotify.net.get_playlist_tracks(
                token, playlist_id, offset, limit)
            track_counter -= len(tracks.items)

    @retry_on_exception(max_retries=3, error_handler=on_error_handler)
    async def _playlists(self, token: str, limit: int) -> PlaylistItem:
        """generator function for retrieving playlists and yielding at one playlist per time

        Args:
            token (str): the spotify access token
            limit (int): the maximum amount of playlists per request

        Yields:
            Playlist: the spotify.validators.playlists.Playlist object
        """
        offset = 0
        playlists = await spotify.net.get_playlists(token, offset=offset, limit=limit)
        playlists_counter = playlists.total
        total_playlists = playlists.total
        while playlists_counter > 0:
            for playlist in playlists.items:
                yield playlist
            offset += limit
            if offset > total_playlists:
                break
            playlists = await spotify.net.get_playlists(
                token, offset=offset, limit=limit)
            playlists_counter -= len(playlists.items)

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
        # callback to the main event handler
        self.app_callback = callback
        # create a backup entry to the sqlite3 database
        backup_id: int = await self.add_backup(backup_name, backup_description)
        # temporary storage for holding tasks
        self.playlist_tasks = []
        self.track_tasks = []
        try:
            async for playlist in await self._playlists(token, limit):
                # callback(BackupEventType.BACKUP_PLAYLIST_ADDED, {"playlist": playlist})
                playlist_id = await self.insert_playlist_db(playlist, backup_id)
                self.playlist_tasks.append(
                    self.insert_playlist_db(playlist, backup_id))
                tracks = self._tracks(
                    token=token, playlist_id=playlist.id, limit=50)
                async for track_item in tracks:
                    self.track_tasks.append(
                        self.insert_track_db(item=track_item, playlist_id=playlist_id))
                    # self.track_tasks.append(print(track_item.track.name))
                if len(self.playlist_tasks) >= MAX_PLAYLISTS_CONNECT:
                    # gather will call create_task automatically
                    await asyncio.gather(*self.playlist_tasks)
                    self.playlist_tasks = []
                if len(self.track_tasks) >= MAX_TRACKS_CONNECT:
                    # gather will call create_task automatically
                    return_exceptions = await asyncio.gather(*self.track_tasks)
                    self.track_tasks = []
            if self.playlist_tasks:
                return_exceptions = await asyncio.gather(*self.playlist_tasks)
                globals.logger.console(return_exceptions.__str__(), "error")
            if self.track_tasks:
                await asyncio.gather(*self.track_tasks)

            callback(BackupEventType.BACKUP_SUCCESS, {})
        except Exception as err:
            globals.logger.console(err.__str__(), "error")

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
            # cursor.execute(
            #     "SELECT id from Backups WHERE date_added = ?", (date_added,))
            # result: any = cursor.fetchone()[0]
            id: int = cursor.lastrowid
            return id

    async def insert_playlist_db(self, item: PlaylistItem, backup_id: int) -> int:
        """insert the playlist into the database file

        Args:
            playlist (Playlist): the playlist object to add
            backup_id (int): the primary key of the backup to associate to

        Returns:
            int: the ID of the playlist
        """
        with BackupSQlite(self.db_path) as cursor:
            cursor.execute('''
            INSERT INTO Playlists 
            (playlist_id, uri, name, description, total_songs, backup_id) VALUES 
            (?, ?, ?, ?, ?, ?)''',
                           (item.id, item.uri, item.name, item.description, item.tracks.total, backup_id))
            playlist_id = cursor.lastrowid
            return playlist_id

    async def insert_track_db(self, item: TrackItem, playlist_id: int) -> int:
        with BackupSQlite(self.db_path) as cursor:
            # ADD THE ALBUM FIRST
            cursor.execute('''
            INSERT INTO Albums (name) VALUES (?)''', (item.track.album.name,))
            album_id = cursor.lastrowid
            artist_names = list(
                map(lambda artist: artist.name, item.track.artists))
            artist_names = ",".join(artist_names)
            # JOIN THE ARTISTS TOGETHER AND ADD THEM
            cursor.execute('''
            INSERT INTO Artists (name) VALUES (?)''', (artist_names,))
            artists_id = cursor.lastrowid
            # NOW ADD THE TRACK INFORMATION
            cursor.execute('''
            INSERT INTO Tracks 
            (uri, name, playlist_id, artists_id, album_id) VALUES 
            (?, ?, ?, ?, ?)''', (item.track.uri, item.track.name, playlist_id, artists_id, album_id))
            track_id = cursor.lastrowid
            globals.logger.console(
                f"Track: {item.track.name} has been stored")
            return track_id

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
            await self.create_playlists_table(cursor)
            await self.create_album_table(cursor)
            await self.create_artists_table(cursor)
            await self.create_track_table(cursor)

    async def create_backup_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Backups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        description TEXT,
                        date_added DATETIME NOT NULL);''')

    async def create_playlists_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''CREATE TABLE IF NOT EXISTS Playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id TEXT NOT NULL,
            uri TEXT NOT NULL,
            name TEXT,
            description TEXT,
            total_songs INTEGER,
            backup_id INTEGER,
            FOREIGN KEY (backup_id) REFERENCES Backups(id));
        ''')

    async def create_track_table(self, cursor: sqlite3.Cursor):
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Tracks (
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
        CREATE TABLE IF NOT EXISTS Albums(
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

async def backup_playlists(
        playlists_todo: Playlists,
        token: str, 
        callback: BACKUP_CALLBACK_TYPE,
        name: str,
        description: str,
        playlist_manager: PlaylistManager):
    pass


if __name__ == '__main__':
    import asyncio
    asyncio.run(_test())
