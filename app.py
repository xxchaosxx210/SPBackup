import wx
import asyncio
import os
import multiprocessing

from ui.main_frame import MainFrame
from ui.dialogs.auth import AuthDialog
from ui.dialogs.user import show_user_info_dialog

import settings

from spotify.listener import RedirectListener
from spotify.listener import PORT
from spotify.net import authorize
from spotify.net import get_playlists
from spotify.net import get_user_info
from spotify.net import get_playlist
from spotify.net import SpotifyError
from spotify.serializers.playlist_info import Playlist as PlaylistInfo
import spotify.const as const

import logging

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger()

class SPBackupApp(wx.App):

    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)
        self.frame = None
    
    def OnInit(self):
        return super().OnInit()

    def run_background_auth_check(self):
        self.token = settings.load()["token"]
        if not self.token:
            logger.info("No Token found. Requesting Authorization...")
            self.start_listening_for_redirect()
        else:
            logger.info("Token found. Retrieving Playlists from User...")
            asyncio.run(self.retrieve_playlists())
    
    async def retrieve_playlists(self):
        try:
            response = await get_playlists(self.token)
        except SpotifyError as err:
            self.handle_spotify_error(error=err)
            return
        wx.CallAfter(self.frame.main_panel.playlists_spw.playlists_ctrl.populate, playlists=response)
        wx.CallAfter(self.frame.sbar.SetStatusText, text="Loaded Playlists successfully")
    
    async def retrieve_user_info(self):
        try:
            response = await get_user_info(self.token)
            wx.CallAfter(show_user_info_dialog, parent=self.frame, userinfo=response)
        except SpotifyError as err:
            self.handle_spotify_error(error=err)
    
    async def retrieve_playlist(self, playlist_id: int):
        try:
            response: PlaylistInfo  = await get_playlist(self.token, playlist_id)
        except SpotifyError as err:
            self.handle_spotify_error(error=err)
    
    def handle_spotify_error(self, error: SpotifyError):
        if error.code == 401:
            wx.CallAfter(self.frame.sbar.SetStatusText, text=error.response_text)
            settings.remove()
            self.start_listening_for_redirect()
        elif error.code == 403:
            self.show_error(error.response_text)
            settings.remove()
        else:
            wx.CallAfter(self.frame.sbar.SetStatusText, text=error.response_text)                
    
    def on_listener_response(self, status: str, value: any):
        if status == "token":
            # save the token to file
            settings.save(value)
            self.token = value
            wx.CallAfter(self.destroy_auth_dialog)
            wx.CallAfter(self.frame.sbar.SetStatusText, "Retrieving Playlists...")
            asyncio.run(self.retrieve_playlists())
        elif status == "authorize":
            loop = asyncio.new_event_loop()
            url = loop.run_until_complete(authorize((
                const.PLAYLIST_MODIFY_PUBLIC,
                const.PLAYLIST_MODIFY_PRIVATE,
                const.PLAYLIST_READ_COLLABORATIVE,
                const.PLAYLIST_READ_PRIVATE
            )))
            wx.CallAfter(self.open_auth_dialog, url=url)
        elif status == "spotify-error":
            wx.CallAfter(self.frame.sbar.SetStatusText, value.response_text)
            wx.CallAfter(self.destroy_auth_dialog)

    def open_auth_dialog(self, url):
        self.auth_dialog = AuthDialog(self.frame, url)
        self.auth_dialog.ShowModal()
    
    def destroy_auth_dialog(self):
        self.auth_dialog.Destroy()
    
    def start_listening_for_redirect(self):
        """listen on the authorization redirect on port 3000
        should return a token
        """
        if not hasattr(self, "listener") or not self.listener.is_alive():
            self.listener = RedirectListener(
                PORT, 
                const.CLIENT_ID, 
                const.CLIENT_SECRET,
                self.on_listener_response)
            self.listener.start()
    
    def show_error(self, message: str):
        # Create the message dialog
        dlg = wx.MessageDialog(self.frame, message, "Error", wx.OK | wx.ICON_ERROR)
        # Show the dialog and wait for the user to click "OK"
        dlg.ShowModal()
        # Destroy the dialog
        dlg.Destroy()


def run_app():
    multiprocessing.freeze_support()
    spbackup_app = SPBackupApp()
    frame = MainFrame(app=spbackup_app, parent=None, title="Spotify Backup - coded by Paul Millar")
    frame.Show()
    spbackup_app.frame = frame
    spbackup_app.run_background_auth_check()
    spbackup_app.MainLoop()

if __name__ == '__main__':
    run_app()