import sqlalchemy
import sqlalchemy.ext.declarative
from sqlalchemy.orm import sessionmaker


Base = sqlalchemy.ext.declarative.declarative_base()


class Backup(Base):
    __tablename__ = 'backups'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    date_added = sqlalchemy.Column(sqlalchemy.DateTime)


class Playlist(Base):
    __tablename__ = 'playlists'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    playlist_id = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    uri = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)
    total_songs = sqlalchemy.Column(sqlalchemy.Integer)
    backup_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('backups.id'))


class Track(Base):
    __tablename__ = 'tracks'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    uri = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    playlist_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('playlists.id'))
    artists_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('artists.id'))
    album_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey('albums.id'))


class Album(Base):
    __tablename__ = 'albums'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)


class Artist(Base):
    __tablename__ = 'artists'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)


def load_engine(db_path: str) -> sqlalchemy.engine.Engine:
    engine = sqlalchemy.create_engine(f'sqlite:///{db_file_path}')
    Base.metadata.create_all(bind=engine)
    return engine


def reload_engine(engine: sqlalchemy.engine.Engine, new_db_path: str) -> sqlalchemy.engine.Engine:
    engine.dispose()
    return load_engine(new_db_path)
