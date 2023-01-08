import threading
from spotify.validators.playlist_info import PlaylistInfo
from spotify.validators.playlist_info import Tracks
from spotify.validators.playlists import Playlists


class UI:

    # store our wxcontrols

    playlists_ctrl = None
    playlistinfo_ctrl = None
    playlists_toolbar = None
    playlistinfo_toolbar = None
    playlists_spw = None
    statusbar = None


class State:

    # holds general global state

    _token: str = None
    _playlist: PlaylistInfo = None 
    _lock = threading.Lock()
    _playlists: Playlists = None

    @staticmethod
    def set_playlists(playlists: Playlists):
        with State._lock:
            State._playlists = playlists

    @staticmethod
    def get_playlists() -> Playlists:
        with State._lock:
            return State._playlists

    @staticmethod
    def set_playlist(playlist: PlaylistInfo):
        with State._lock:
            State._playlist = playlist
    
    @staticmethod
    def update_playlist_tracks(tracks: Tracks):
        """update the tracks in the playlist info

        Args:
            tracks (Tracks): tracks to be updated
        """
        with State._lock:
            State._playlist.tracks = tracks
    
    @staticmethod
    def get_playlist() -> PlaylistInfo:
        with State._lock:
            return State._playlist
    
    @staticmethod
    def set_token(token: str):
        with State._lock:
            State._token = token
    
    @staticmethod
    def get_token() -> str:
        with State._lock:
            return State._token