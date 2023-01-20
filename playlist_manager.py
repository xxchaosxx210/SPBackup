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
from typing import (
    Callable,
    Dict,
    Union
)

import spotify.debugging
import spotify.net
import spotify.constants
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlists import Item as PlaylistItem
from spotify.validators.playlists import Playlists
from spotify.validators.tracks import Item as TrackItem
from spotify.validators.tracks import Tracks

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


class BackupEventType(Enum):
    """for our function callback

    Args:
        Enum (int): ID of the event that has happened
    """

    # when the backup starts
    BACKUP_START = enum_auto()
    # when playlists info is retrieved at the beginning. Basic information like total
    PLAYLISTS_UPDATE = enum_auto()
    # playlist found added to database
    PLAYLIST_ADDED = enum_auto()
    # playlist information including total tracks
    PLAYLIST_UPDATE = enum_auto()
    # Track found and added to database
    TRACK_ADDED = enum_auto()
    # Backup was successful
    BACKUP_SUCCESS = enum_auto()
    # spotify blocking more requests
    MAX_LIMIT_RATE_REACHED_RETRY = enum_auto()

    # errors
    DATABASE_ERROR = enum_auto()
    NETWORK_ERROR = enum_auto()


BACKUP_CALLBACK_TYPE = Callable[[BackupEventType, Union[Dict, str]], None]


class BackupSQlite:

    """Backup Context Manager for connecting to the database
    """

    def __init__(self, filepath, error_handler) -> None:
        self.filepath = filepath
        self.error_handler = error_handler

    def __enter__(self, *args, **kwargs) -> sqlite3.Cursor:
        self.conn = sqlite3.connect(self.filepath)
        return self.conn.cursor()

    def __exit__(self, type: Exception, value: any, exception: object):
        self.conn.commit()
        self.conn.close()
        if type:
            self.error_handler(type, value, exception)
            return False
        return True


def retry_on_limit_exceeded(delay: int, timeout_factor: float):
    """retries if spotify responds with limit exceeded code
    will sleep for delay period timeout_factor gets added on everytime
    the response is 428 code

    Args:
        delay (int): the start delay in seconds
        timeout_factor (float): the timeout factor to be added on after every unsuccessful request
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # decorator arguments need to be declared in this local scope
            nonlocal delay
            nonlocal timeout_factor
            default_delay = delay
            # infinte loop may change this later on but for now the function will keep
            # looping on every unsuccessful 428 code resquest
            while True:
                try:
                    result = await func(*args, **kwargs)
                    delay = default_delay
                    return result
                except Exception as e:
                    # check for a maximum limit exceeded from the server
                    if isinstance(e, spotify.net.SpotifyError) and \
                            e.code == spotify.constants.STATUS_LIMIT_RATE_REACHED:
                        task_name: str = asyncio.current_task().get_name()
                        # callback()
                        PlaylistManager.backup_callback(
                            BackupEventType.MAX_LIMIT_RATE_REACHED_RETRY, {
                                "delay": delay,
                                "timeout_factor": timeout_factor,
                                "task_name": task_name
                            })
                        await asyncio.sleep(delay)
                        delay += timeout_factor
                    else:
                        raise e
        return wrapper
    return decorator


class PlaylistManager:

    running_task: asyncio.Task = None
    backup_callback: BACKUP_CALLBACK_TYPE = None

    def __init__(self) -> None:
        # settings ans setting up the database tables
        global PLAYLIST_DIR
        self.user: SpotifyUser = None
        self.db_path: str = ""
        PLAYLIST_DIR = os.path.join(
            spotify.debugging.APP_SETTINGS_DIR, PLAYLIST_PATHNAME)
        # main callback handler
        PlaylistManager.backup_callback: BACKUP_CALLBACK_TYPE = None
        self.token: str = ""
        self.playlist_request_limit = 50
        self.tracks_request_limit = 50
        self.max_playlists_tasks = 1
        self.max_tracks_tasks = 1

    async def backup_playlists(
            self,
            token: str,
            callback: BACKUP_CALLBACK_TYPE,
            backup_name: str,
            backup_description: str):
        """the start of the backup process. Call this from within the main thread

        Args:
            callback (BACKUP_CALLBACK_TYPE): the callback to the main thread
        """
        PlaylistManager.backup_callback = callback
        self.token = token
        # insert the backup table here
        backup_pk: int = await self.add_backup(
            name=backup_name, description=backup_description)
        # get the playlist information
        playlists_info: Playlists = await spotify.net.get_playlists(self.token, limit=50)
        await self.handle_playlists(
            backup_pk=backup_pk,
            playlist_info=playlists_info, limit=50)
        callback(BackupEventType.BACKUP_SUCCESS, None)

    @retry_on_limit_exceeded(delay=1, timeout_factor=0.1)
    async def get_playlists_with_retry(self, *args, **kwargs) -> Playlists:
        return await spotify.net.get_playlists(*args, **kwargs)

    @retry_on_limit_exceeded(delay=1, timeout_factor=0.1)
    async def get_tracks_with_retry(self, *args, **kwargs) -> Tracks:
        return await spotify.net.get_playlist_tracks(*args, **kwargs)

    async def fetch_and_insert_tracks(
            self,
            playlist_pk: int,
            playlist_id: str,
            offset: int,
            limit_per_request: int):
        """get the next tracks listing from the offset and loop through each track and store to
        the database

        Args:
            playlist_id (str): ID of the playlist to get the tracks from
            offset (int): the current offset
            limit_per_request (int): the amount of tracks to return (Maximum is 50)
        """
        # globals.logger.console(
        #     f'Fetching next tracks from Playlist ID {playlist_id} offset: {offset}')
        tracks = await self.get_tracks_with_retry(
            access_token=self.token,
            playlist_id=playlist_id,
            offset=offset,
            limit=limit_per_request
        )
        for item in tracks.items:
            # insert into database here
            await self.insert_track_db(item=item, playlist_pk=playlist_pk)
            try:
                PlaylistManager.backup_callback(
                    BackupEventType.BACKUP_TRACK_ADDED, {
                        "item": item,
                        "tracks": tracks
                    }
                )
            except Exception as err:
                globals.logger.console(f'Error calling backup_callback in fetch_and_insert_tracks. Reason: {err.__str__()}')

    async def handle_tracks(
            self,
            playlist_pk: int,
            playlist_item: PlaylistItem,
            limit_per_request: int):
        """is the tracks handler for the current playlist that requires pagination
        change self.max_tracks_tasks to increase or decrease the amount of connections

        Args:
            playlist_item (PlaylistItem): the playlist item to get the track listings from
            limit_per_request (int): the amount of tracks to return from the request
        """
        # keeps track of the loop offset and checks limit and total
        # creates a new fetch_and_insert_tracks
        offset = 0
        fetch_tasks = []
        for tracks_index in range(playlist_item.tracks.total):
            loop = asyncio.get_event_loop()
            task: asyncio.Task = loop.create_task(self.fetch_and_insert_tracks(
                playlist_pk=playlist_pk,
                playlist_id=playlist_item.id,
                offset=offset,
                limit_per_request=limit_per_request))
            fetch_tasks.append(task)
            if len(fetch_tasks) >= self.max_tracks_tasks:
                result = asyncio.gather(*fetch_tasks, return_exceptions=True)
                await result
                fetch_tasks = []
                offset += limit_per_request
        if fetch_tasks:
            await asyncio.gather(*fetch_tasks, return_exceptions=True)

    async def fetch_and_insert_playlists(
            self, backup_pk: int, offset: int, limit: int):
        """ loop through each offset and retrieve the playlists and add each playlist to the database
        and start the next tracks handler for retrieving the tracks

        Args:
            backup_pk (int): The Backup Primary Key in the database to be associated with each playlist
            offset (int): the offset to loop through handle pagination
            limit (int): limit the amount in the respoonse
        """
        playlists = await self.get_playlists_with_retry(
            token=self.token, url="", offset=offset, limit=limit)
        for playlist_item in playlists.items:
            # Insert the Playlist to the database
            playlist_pk = await self.insert_playlist_db(
                item=playlist_item, backup_id=backup_pk)
            # handle the playlist pagination
            await self.handle_tracks(
                playlist_pk=playlist_pk,
                playlist_item=playlist_item,
                limit_per_request=limit)

    async def handle_playlists(
            self,
            backup_pk: int,
            playlist_info: Playlists,
            limit=50):
        offset = 0
        tasks = []
        for index in range(playlist_info.total):
            loop = asyncio.get_event_loop()
            tasks.append(loop.create_task(
                self.fetch_and_insert_playlists(backup_pk, offset, limit)))
            if len(tasks) >= self.max_playlists_tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                tasks = []
                offset += limit
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def on_database_error(self, type, value, exception):
        PlaylistManager.backup_callback(BackupEventType.DATABASE_ERROR, {
            "type": type,
            "value": value,
            "exception": exception})

    async def add_backup(self, name: str, description: str) -> int:
        """adds a backup entry to the database file

        Args:
            name (str): Name of the backup
            description (str): brief description of the backup. Can be empty

        Returns:
            int: the Backup Primary Key ID
        """
        date_added = datetime.now()
        with BackupSQlite(self.db_path, self.on_database_error) as cursor:
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
        with BackupSQlite(self.db_path, self.on_database_error) as cursor:
            cursor.execute('''
            INSERT INTO Playlists 
            (playlist_id, uri, name, description, total_songs, backup_id) VALUES 
            (?, ?, ?, ?, ?, ?)''',
                           (item.id, item.uri, item.name, item.description, item.tracks.total, backup_id))
            playlist_id = cursor.lastrowid
            return playlist_id

    async def insert_track_db(self, item: TrackItem, playlist_pk: int) -> int:
        with BackupSQlite(self.db_path, self.on_database_error) as cursor:
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
            (?, ?, ?, ?, ?)''', (item.track.uri, item.track.name, playlist_pk, artists_id, album_id))
            track_id = cursor.lastrowid
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
        if user is None:
            raise TypeError("User in create_backup_directory does not exist")
        self.user = user
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
        with BackupSQlite(self.db_path, self.on_database_error) as cursor:
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
