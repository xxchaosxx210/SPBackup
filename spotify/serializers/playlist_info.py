from typing import List, Optional
from pydantic import BaseModel

class Artist(BaseModel):
    name: str

class ExternalURL(BaseModel):
    spotify: str

class Image(BaseModel):
    height: Optional[int]
    url: str
    width: Optional[int]

class Owner(BaseModel):
    display_name: str
    external_urls: ExternalURL
    href: str
    id: str
    type: str
    uri: str

class Track(BaseModel):
    artists: List[Artist]
    available_markets: List[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_urls: ExternalURL
    href: str
    id: str
    is_local: bool
    name: str
    preview_url: Optional[str]
    track_number: int
    type: str
    uri: str

class PlaylistTrack(BaseModel):
    added_at: str
    added_by: Owner
    is_local: bool
    track: Track

class Playlist(BaseModel):
    collaborative: bool
    description: Optional[str]
    external_urls: ExternalURL
    followers: Optional[dict]
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Owner
    primary_color: Optional[str]
    public: Optional[bool]
    snapshot_id: str
    tracks: Optional[dict]
    type: str
    uri: str
