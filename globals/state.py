"""
state.py

    Holds global state for the SPBackup Application
"""

import threading
import wx

from spotify.validators.playlist import Playlist
from spotify.validators.playlist import Tracks as PlaylistTracks
from spotify.validators.playlists import Playlists

from playlist_manager import PlaylistManager


class UI:

    """UI holds the wxwindow controls for easier reference
    """

    # store our wxcontrols instances

    main_frame: wx.Frame = None
    playlists_ctrl: wx.ListCtrl = None
    tracksctrl: wx.ListCtrl = None
    playlists_toolbar: wx.Panel = None
    playlistinfo_toolbar: wx.Panel = None
    playlists_spw: wx.SplitterWindow = None
    statusbar: wx.StatusBar = None
    progress_dialog: wx.Dialog = None


class Global:

    __lock: threading.Lock = threading.Lock()

    @staticmethod
    def get_lock():
        return Global.__lock


class User(Global):

    __token: str = None

    @staticmethod
    def set_token(token: str):
        with Global.get_lock():
            User.__token = token

    @staticmethod
    def get_token() -> str:
        with Global.get_lock():
            return User.__token

class State(Global):

    _playlist: Playlist = None 
    _playlists: Playlists = None
    playlist_manager: PlaylistManager = None

    @staticmethod
    def set_playlists(playlists: Playlists):
        with Global.get_lock():
            State._playlists = playlists

    @staticmethod
    def get_playlists() -> Playlists:
        with Global.get_lock():
            return State._playlists

    @staticmethod
    def set_playlist(playlist: Playlist):
        with Global.get_lock():
            State._playlist = playlist
    
    @staticmethod
    def update_playlist_tracks(tracks: PlaylistTracks):
        """update the tracks in the playlist info

        Args:
            tracks (Tracks): tracks to be updated
        """
        with Global.get_lock():
            State._playlist.tracks = tracks
    
    @staticmethod
    def get_playlist_tracks():
        with Global.get_lock():
            return State._playlist.tracks
    
    @staticmethod
    def get_playlist() -> Playlist:
        with Global.get_lock():
            return State._playlist
