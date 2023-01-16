"""
playlist_manager.py - handles the users playlists and backs up and restores them using sqlite3
and json
"""

import sqlite3
import os
import time
import asyncio

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


class PlaylistManager:

    def __init__(self) -> None:
        # settings ans setting up the database tables
        global PLAYLIST_DIR
        self.user: SpotifyUser = None
        self.db_path: str = ""
        PLAYLIST_DIR = os.path.join(
            spotify.debugging.APP_SETTINGS_DIR, PLAYLIST_PATHNAME)

        # for gathering playlists and tracks
        self.queue = asyncio.Queue()
        self.tasks = []
        self.done = False

    async def playlists(self, token: str, limit: int):
        """generator function for retrieving playlists and yielding at one playlist per time

        Args:
            token (str): _description_
            limit (int): _description_

        Yields:
            _type_: _description_
        """
        offset = 0
        playlists = await spotify.net.get_playlists(
            token,
            offset=offset,
            limit=limit)
        playlists = playlists.items
        total_playlists = playlists.total
        while total_playlists > 0:
            for playlist in playlists:
                yield playlist
            offset += limit
            playlists = await spotify.net.get_playlists(
                token, offset=offset, limit=limit)
            total_playlists -= len(playlists.items)

    async def backup_playlists(self,
                               token: str,
                               limit: int = 50):
        # temporary storage for holding tasks
        self.tasks = []
        async for playlist in self.playlists(token, limit):
            self.tasks.append(
                self.insert_playlist_db(playlist))
            if len(self.tasks) >= MAX_PLAYLISTS_CONNECT:
                # gather will call create_task automatically
                await asyncio.gather(*self.tasks)
                self.tasks = []
        if self.tasks:
            await asyncio.gather(*self.tasks)

    async def insert_playlist_db(self, playlist: Playlist):
        print(playlist.name)

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
