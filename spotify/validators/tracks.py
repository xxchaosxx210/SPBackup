# The Tracks basemodel represents the https://api.spotify.com/v1/{playlistid}/tracks

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
    external_urls: Optional[ExternalUrls]
    href: Optional[str]
    id: Optional[str]
    name: Optional[str]
    type: Optional[str]
    uri: Optional[str]


class Image(BaseModel):
    height: Optional[int]
    url: str
    width: Optional[int]


class Album(BaseModel):
    album_type: Optional[str]
    artists: List[Artist]
    available_markets: Optional[List[str]]
    external_urls: Optional[ExternalUrls]
    href: Optional[str]
    id: Optional[str]
    images: Optional[List[Image]]
    name: Optional[str]
    release_date: Optional[str]
    release_date_precision: Optional[str]
    total_tracks: Optional[int]
    type: Optional[str]
    uri: Optional[str]


class ExternalIds(BaseModel):
    isrc: Optional[str]


class Track(BaseModel):
    album: Optional[Album]
    artists: Optional[List[Artist]]
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
    url: Optional[Any]


class Item(BaseModel):
    added_at: str
    added_by: AddedBy
    is_local: bool
    primary_color: Any
    track: Optional[Track]
    video_thumbnail: Optional[VideoThumbnail]

    # Ive been working on a playlist backup app and had to add these property methods in
    # to deal with podcasts. As they do not contain tracks. Something I need to look at

    @property
    def track_name(self):
        return self.track.name if self.track is not None else ""

    @property
    def track_album(self):
        return self.track.album

    @property
    def track_uri(self) -> str:
        return self.track.uri if self.track is not None else ""

    @property
    def track_album_name(self) -> str:
        return self.track.album.name if self.track is not None else ""

    @property
    def track_artists_names(self) -> list:
        return self.track.artists if self.track is not None else []


class Tracks(BaseModel):
    href: str
    items: List[Item]
    limit: int
    next: Any
    offset: int
    previous: Any
    total: int
