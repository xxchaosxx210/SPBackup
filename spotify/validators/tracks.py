from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str


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


class ExternalIds(BaseModel):
    isrc: str


class ExternalUrls4(BaseModel):
    spotify: str


class Track(BaseModel):
    album: Album
    artists: List[Artist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    episode: bool
    explicit: bool
    external_ids: ExternalIds
    external_urls: ExternalUrls4
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
    added_at: str
    added_by: AddedBy
    is_local: bool
    primary_color: Any
    track: Track
    video_thumbnail: VideoThumbnail


class Tracks(BaseModel):
    href: str
    items: List[Item]
    limit: int
    next: Any
    offset: int
    previous: Any
    total: int
