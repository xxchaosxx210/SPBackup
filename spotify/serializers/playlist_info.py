from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str = ""


class Artist(BaseModel):
    external_urls: Optional[ExternalUrls]
    href: str = ""
    id: str = ""
    name: str = ""
    type: str = ""
    uri: str = ""


class Image(BaseModel):
    height: Optional[int]
    url: str = ""
    width: Optional[int]


class Album(BaseModel):
    album_type: str = ""
    artists: List[Artist] = []
    available_markets: List[str] = []
    _external_urls: ExternalUrls = None
    href: str = ""
    id: str = ""
    images: List[Image] = []
    name: str = ""
    release_date: Optional[str]
    release_date_precision: Optional[str]
    total_tracks: int = 0
    type: str = ""
    uri: str = ""


class Track(BaseModel):
    album: Album = None
    artists: List[Artist] = []
    href: str = ""
    name: str = ""
    uri: str = ""


class Item(BaseModel):
    added_at: str = ""
    track: Optional[Track] = None

    @property
    def track_name(self):
        return self.track.name if self.track is not None else ""
    
    @property
    def track_album(self):
        return self.track.album if self.track is not None else Album()


class Tracks(BaseModel):
    items: List[Item] = []
    next: Any = ""
    offset: int = 0
    previous: Any = ""
    total: int = 0


class PlaylistInfo(BaseModel):
    name: str = ""
    tracks: Tracks = []
    id: str
