"""
playlist_manager.py - handles the users playlists and backs up and restores them using sqlite3
and json
"""

import os
import asyncio
from enum import (
    Enum,
    auto as enum_auto
)
from typing import (
    Callable,
    Dict,
    Union,
    List
)

import aiosqlite

import spotify.debugging
import spotify.net
import spotify.constants
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlists import Item as PlaylistItem
from spotify.validators.playlists import Playlists
from spotify.validators.tracks import Tracks

from database import LocalDatabase

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
    # General error coming from gather function
    BACKUP_ERROR = enum_auto()

    # errors
    DATABASE_ERROR = enum_auto()
    NETWORK_ERROR = enum_auto()


BACKUP_CALLBACK_TYPE = Callable[[BackupEventType, Union[Dict, str]], None]


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
        self.local_db: LocalDatabase = None
        PLAYLIST_DIR = os.path.join(
            spotify.debugging.APP_SETTINGS_DIR, PLAYLIST_PATHNAME)
        # main callback handler
        PlaylistManager.backup_callback: BACKUP_CALLBACK_TYPE = None
        self.token: str = ""
        self.playlist_request_limit = 50
        self.tracks_request_limit = 50
        self.max_playlists_tasks = 5
        self.max_tracks_tasks = 5

    def handle_error_results_from_gather(self, function_name: str, results: List[Exception]):
        for result in results:
            if result is None:
                continue
            if isinstance(result, Exception):
                self.backup_callback(BackupEventType.BACKUP_ERROR, {
                    "error": result.__str__(),
                    "function_name": function_name,
                    "type": type(result)
                })

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
        try:
            PlaylistManager.backup_callback = callback
            self.token = token
            # create the database tables if none exist
            await self.local_db.create_tables()
            # insert the backup table here
            backup_pk: int = await self.local_db.add_backup(
                name=backup_name, description=backup_description)
            # get the playlist information
            playlists_info: Playlists = await spotify.net.get_playlists(self.token, limit=50)
            # notify the main thread that backup is starting
            current_task = asyncio.current_task(asyncio.get_event_loop())
            self.backup_callback(BackupEventType.BACKUP_START, {
                "playlists_info": playlists_info,
                "tasks": [current_task]
            })
            await self.handle_playlists(
                backup_pk=backup_pk,
                playlist_info=playlists_info, limit=50)
            callback(BackupEventType.BACKUP_SUCCESS, None)
        except Exception as err:
            self.backup_callback(BackupEventType.BACKUP_ERROR, {
                "error": err})
        finally:
            return

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
        tracks = await self.get_tracks_with_retry(
            access_token=self.token,
            playlist_id=playlist_id,
            offset=offset,
            limit=limit_per_request
        )
        for item in tracks.items:
            # insert into database here
            await self.local_db.insert_track(item=item, playlist_pk=playlist_pk)
            PlaylistManager.backup_callback(
                BackupEventType.TRACK_ADDED, {
                    "item": item,
                    "tracks": tracks
                }
            )

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
        if limit_per_request > playlist_item.tracks.total:
            limit_per_request = playlist_item.tracks.total
        while offset < playlist_item.tracks.total:
            loop = asyncio.get_event_loop()
            task: asyncio.Task = loop.create_task(self.fetch_and_insert_tracks(
                playlist_pk=playlist_pk,
                playlist_id=playlist_item.id,
                offset=offset,
                limit_per_request=limit_per_request))
            fetch_tasks.append(task)
            if len(fetch_tasks) >= self.max_tracks_tasks:
                results: List[any] = await asyncio.gather(*fetch_tasks, return_exceptions=False)
                # self.handle_error_results_from_gather(
                #     "handle_tracks", results=results)
                fetch_tasks = []
            offset += limit_per_request
        if fetch_tasks:
            results: List[any] = await asyncio.gather(*fetch_tasks, return_exceptions=False)
            # self.handle_error_results_from_gather(
            #     "handle_tracks", results=results)

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
            playlist_pk = await self.local_db.insert_playlist(
                item=playlist_item, backup_id=backup_pk)
            self.backup_callback(BackupEventType.PLAYLIST_ADDED, {
                "item": playlist_item
            })
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
        if limit > playlist_info.total:
            limit = playlist_info.total
        while offset <= playlist_info.total:
            loop = asyncio.get_event_loop()
            tasks.append(loop.create_task(
                self.fetch_and_insert_playlists(backup_pk, offset, limit)))
            if len(tasks) >= self.max_playlists_tasks:
                results: List[any] = await asyncio.gather(*tasks, return_exceptions=False)
                # self.handle_error_results_from_gather(
                #     "handle_playlists", results=results)
                tasks = []
            offset += limit  # Move offset to next page of playlists

        if tasks:
            results: List[any] = await asyncio.gather(*tasks, return_exceptions=False)
            # self.handle_error_results_from_gather(
            #     "handle_playlists", results=results)

    def on_database_error(self, type, value, exception):
        PlaylistManager.backup_callback(BackupEventType.DATABASE_ERROR, {
            "type": type,
            "value": value,
            "exception": exception})

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
            db_path = os.path.join(user_path, DATABASE_FILENAME)
            self.local_db = LocalDatabase(db_path, self.on_database_error)
            return db_path
