from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str


class Followers(BaseModel):
    href: Any
    total: int


class Image(BaseModel):
    height: Optional[int]
    url: Optional[str]
    width: Optional[int]


class Owner(BaseModel):
    display_name: str
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str


class AddedBy(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str


class Artist(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class Album(BaseModel):
    album_type: str
    artists: List[Artist]
    available_markets: List[str]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: Optional[str]
    release_date_precision: Optional[str]
    total_tracks: int
    type: str
    uri: str


class ExternalIds(BaseModel):
    isrc: Optional[str]


class Track(BaseModel):
    album: Album
    artists: List[Artist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    episode: bool
    explicit: bool
    external_ids: ExternalIds
    external_urls: ExternalUrls
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: Optional[str]
    track: bool
    track_number: int
    type: str
    uri: str


class VideoThumbnail(BaseModel):
    url: Any


class Item(BaseModel):
    added_at: Optional[str]
    added_by: Optional[AddedBy]
    is_local: Optional[bool]
    primary_color: Optional[Any]
    track: Optional[Track]
    video_thumbnail: Optional[VideoThumbnail]


class Tracks(BaseModel):
    href: str
    items: List[Item]
    limit: int
    next: Any
    offset: int
    previous: Any
    total: int


class Playlist(BaseModel):
    collaborative: bool
    description: str
    external_urls: ExternalUrls
    followers: Followers
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Owner
    primary_color: Any
    public: bool
    snapshot_id: str
    tracks: Tracks
    type: str
    uri: str
