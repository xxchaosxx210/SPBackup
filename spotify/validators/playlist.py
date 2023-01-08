from pydantic import BaseModel
from typing import List, Optional

class ExternalUrls(BaseModel):
    spotify: str

class User(BaseModel):
    display_name: str
    external_urls: ExternalUrls
    href: str
    id: str
    type: str
    uri: str

class Image(BaseModel):
    height: Optional[int]
    url: str
    width: Optional[int]

class Tracks(BaseModel):
    href: str
    total: int

class Playlist(BaseModel):
    collaborative: bool
    description: str
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    owner: User
    primary_color: Optional[str]
    public: bool
    snapshot_id: str
    tracks: Tracks
    type: str
    uri: str