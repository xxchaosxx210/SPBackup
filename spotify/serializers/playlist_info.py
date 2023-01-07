from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str


class Artist(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class Image(BaseModel):
    height: int
    url: str
    width: int


class Album(BaseModel):
    album_type: str
    artists: List[Artist]
    available_markets: List[str]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str


class Track(BaseModel):
    album: Album
    artists: List[Artist]
    href: str
    name: str
    uri: str


class Item(BaseModel):
    added_at: str
    track: Track


class Tracks(BaseModel):
    items: List[Item]
    next: Any
    offset: int
    previous: Any
    total: int


class PlaylistInfo(BaseModel):
    name: str
    tracks: Tracks
