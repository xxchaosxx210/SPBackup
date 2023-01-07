import threading
from spotify.serializers.playlist_info import PlaylistInfo


class State:

    _token: str = None
    _playlist: PlaylistInfo = None 
    _lock = threading.Lock()

    @staticmethod
    def set_playlist(playlist: PlaylistInfo):
        with State._lock:
            State._playlist = playlist
    
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