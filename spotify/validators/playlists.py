# This is the minimal Playlist information used with get_playlists

from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str = ""


class Image(BaseModel):
    height: Optional[int]
    url: str = ""
    width: Optional[int]


# The owner of the playlist
class Owner(BaseModel):
    display_name: str = ""
    external_urls: Optional[ExternalUrls]
    href: str = ""
    id: str = ""
    type: str = ""
    uri: str = ""


# basic information on the tracks
class Tracks(BaseModel):
    href: str = ""
    total: int = 0


# Playlist Item
class Item(BaseModel):
    collaborative: bool
    description: str
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Optional[Owner]
    primary_color: Any
    public: bool
    snapshot_id: str
    tracks: Tracks = []
    type: str
    uri: str


class Playlists(BaseModel):
    href: str
    items: List[Item] = []
    limit: int
    next: str = None
    offset: int
    previous: str = None
    total: int = 0
