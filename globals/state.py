"""
state.py

    Holds global state for the SPBackup Application
"""

import threading
import wx

from spotify.validators.playlist import Playlist
from spotify.validators.playlist import Tracks as PlaylistTracks
from spotify.validators.playlists import Playlists
from spotify.validators.user import User as SpotifyUser

from ui.dialogs.loading import LoadingDialog
from ui.dialogs.restore import RestoreDialog


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
    progress_dialog: LoadingDialog = None
    restore_dialog: RestoreDialog = None


class Global:

    """
    holds the global lock for async
    """

    __lock: threading.Lock = threading.Lock()

    @staticmethod
    def get_lock():
        return Global.__lock


class UserState(Global):

    """
    currently loaded User information settings state and token
    """

    __token: str = None
    __user: SpotifyUser = None

    @staticmethod
    def set_token(token: str):
        with Global.get_lock():
            UserState.__token = token

    @staticmethod
    def get_token() -> str:
        with Global.get_lock():
            return UserState.__token

    @staticmethod
    def set_user(user: SpotifyUser):
        with Global.get_lock():
            UserState.__user = user
    
    @staticmethod
    def get_user() -> SpotifyUser:
        with Global.get_lock():
            return UserState.__user


class SpotifyState(Global):

    """
    for holding playlists and playlist
    """

    __playlist: Playlist = None
    __playlists: Playlists = None

    @staticmethod
    def set_playlists(playlists: Playlists):
        with Global.get_lock():
            SpotifyState.__playlists = playlists

    @staticmethod
    def get_playlists() -> Playlists:
        with Global.get_lock():
            return SpotifyState.__playlists

    @staticmethod
    def set_playlist(playlist: Playlist):
        with Global.get_lock():
            SpotifyState.__playlist = playlist

    @staticmethod
    def update_playlist_tracks(tracks: PlaylistTracks):
        """update the tracks in the playlist info

        Args:
            tracks (Tracks): tracks to be updated
        """
        with Global.get_lock():
            SpotifyState.__playlist.tracks = tracks

    @staticmethod
    def get_playlist_tracks():
        with Global.get_lock():
            return SpotifyState.__playlist.tracks

    @staticmethod
    def get_playlist() -> Playlist:
        with Global.get_lock():
            return SpotifyState.__playlist
