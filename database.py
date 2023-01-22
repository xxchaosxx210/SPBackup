import os
from datetime import datetime

import aiosqlite

from spotify.validators.user import User as SpotifyUser
from spotify.validators.tracks import Item as TrackItem
from spotify.validators.playlists import Item as PlaylistItem


class BackupSQlite:

    """Backup Context Manager for connecting to the database
    """

    def __init__(self, filepath, error_handler) -> None:
        self.filepath = filepath
        self.error_handler = error_handler

    async def __aenter__(self, *args, **kwargs) -> aiosqlite.Cursor:
        self.conn = await aiosqlite.connect(self.filepath)
        cursor = await self.conn.cursor()
        return cursor

    async def __aexit__(self, type: Exception, value: any, exception: object):
        await self.conn.commit()
        await self.conn.close()
        if type:
            self.error_handler(type, value, exception)
            return False
        return True


class LocalDatabase:

    """local sqlite database class
    """

    def __init__(self, path: str, error_handler: callable) -> None:
        self.path = path
        self.error_handler = error_handler

    async def add_backup(self, name: str, description: str) -> int:
        """adds a backup entry to the database file

        Args:
            name (str): Name of the backup
            description (str): brief description of the backup. Can be empty

        Returns:
            int: the Backup Primary Key ID
        """
        date_added = datetime.now()
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            await cursor.execute('''
                INSERT INTO Backups (name, description, date_added)
                VALUES(?, ?, ?)''', (name, description, date_added))
            # await cursor.execute(
            #     "SELECT id from Backups WHERE date_added = ?", (date_added,))
            # result: any = cursor.fetchone()[0]
            id: int = cursor.lastrowid
            return id

    async def get_backups(self) -> list:
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            await cursor.execute('SELECT * from Backups')
            backups = cursor.fetchall()
            return backups

    async def get_playlists(self, backup_pk: int) -> list:
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            await cursor.execute(f'SELECT * from Playlists WHERE backup_id={backup_pk}')
            playlists = cursor.fetchall()
            return playlists

    async def get_backup_from_date_added(self, date_added: str) -> tuple:
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            await cursor.execute(f'''SELECT * FROM Backups WHERE date_added="{date_added}"''')
            backup = cursor.fetchone()
            return backup

    async def insert_playlist_db(self, item: PlaylistItem, backup_id: int) -> int:
        """insert the playlist into the database file

        Args:
            playlist (Playlist): the playlist object to add
            backup_id (int): the primary key of the backup to associate to

        Returns:
            int: the ID of the playlist
        """
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            await cursor.execute('''
            INSERT INTO Playlists 
            (playlist_id, uri, name, description, total_songs, backup_id) VALUES 
            (?, ?, ?, ?, ?, ?)''',
                                 (item.id, item.uri, item.name, item.description, item.tracks.total, backup_id))
            playlist_id = cursor.lastrowid
            return playlist_id

    async def insert_track_db(self, item: TrackItem, playlist_pk: int) -> int:
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            if item.track is None:
                pass
            artist_names = list(
                map(lambda artist: artist.name, item.track_artists_names))
            artist_names = ",".join(artist_names)
            # ADD THE ALBUM FIRST
            await cursor.execute('''
            INSERT INTO Albums (name) VALUES (?)''', (item.track_album_name,))
            album_id = cursor.lastrowid
            # JOIN THE ARTISTS TOGETHER AND ADD THEM
            await cursor.execute('''
            INSERT INTO Artists (name) VALUES (?)''', (artist_names,))
            artists_id = cursor.lastrowid
            # NOW ADD THE TRACK INFORMATION
            await cursor.execute('''
            INSERT INTO Tracks 
            (uri, name, playlist_id, artists_id, album_id) VALUES 
            (?, ?, ?, ?, ?)''', (item.track_uri, item.track_name, playlist_pk, artists_id, album_id))
            track_id = cursor.lastrowid
            return track_id

    async def create_tables(self):
        async with BackupSQlite(self.path, self.error_handler) as cursor:
            # setup the database
            await self.create_backup_table(cursor)
            await self.create_playlists_table(cursor)
            await self.create_album_table(cursor)
            await self.create_artists_table(cursor)
            await self.create_track_table(cursor)

    async def create_backup_table(self, cursor: aiosqlite.Cursor):
        await cursor.execute('''CREATE TABLE IF NOT EXISTS Backups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        description TEXT,
                        date_added DATETIME NOT NULL);''')

    async def create_playlists_table(self, cursor: aiosqlite.Cursor):
        await cursor.execute('''CREATE TABLE IF NOT EXISTS Playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id TEXT NOT NULL,
            uri TEXT NOT NULL,
            name TEXT,
            description TEXT,
            total_songs INTEGER,
            backup_id INTEGER,
            FOREIGN KEY (backup_id) REFERENCES Backups(id));
        ''')

    async def create_track_table(self, cursor: aiosqlite.Cursor):
        await cursor.execute('''
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

    async def create_album_table(self, cursor: aiosqlite.Cursor):
        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS Albums(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        ''')

    async def create_artists_table(self, cursor: aiosqlite.Cursor):
        await cursor.execute('''
        CREATE TABLE IF NOT EXISTS Artists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        );
        ''')
