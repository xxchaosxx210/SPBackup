import wx
import asyncio
import multiprocessing
import argparse

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
from spotify.serializers.playlist_info import PlaylistInfo
import spotify.const as const


from spotify.debug import debug as spotify_debug
import utils.logger as logger


class SPBackupApp(wx.App):

    NAME = "SPBackup"

    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)
        self.frame = None
    
    def OnInit(self):
        return super().OnInit()

    def run_background_auth_check(self):
        self.token = settings.load()["token"]
        if not self.token:
            logger.console("No Token found. Requesting Authorization...", "info")
            self.start_listening_for_redirect()
        else:
            logger.console("Token found. Retrieving Playlists from User...", "info")
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
            playlist: PlaylistInfo  = await get_playlist(self.token, playlist_id)
            wx.CallAfter(
                self.frame.main_panel.playlists_spw.playlistinfo_ctrl.populate, playlist=playlist
            )
        except SpotifyError as err:
            self.handle_spotify_error(error=err)
    
    def handle_spotify_error(self, error: SpotifyError):
        """handle the error status codes recieved from Spotify

        Args:
            error (SpotifyError): exceptioon object
        """
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
        """response from the RedirectListener

        Args:
            status (str): read the RedirectListener EVENT for documentation
            value (any): depends on status. If an error then it will be error object else json
        """
        if status == RedirectListener.EVENT_TOKEN_RECIEVED:
            # We have authentication save the token and use until 401 error again and restart this process again to obtain another token
            # save the token to file
            settings.save(value)
            self.token = value
            logger.console("Response from RedirectListener: Token recieved", "info")
            wx.CallAfter(self.destroy_auth_dialog)
            wx.CallAfter(self.frame.sbar.SetStatusText, "Retrieving Playlists...")
            asyncio.run(self.retrieve_playlists())
        elif status == RedirectListener.EVENT_REQUESTING_AUTHORIZATION:
            # We need a new token. create a new playlist scope and request from Spotify a new Token
            # Prompt user to follow Url
            logger.console("Response from RedirectListener: Requesting Authorization...", "info")
            loop = asyncio.new_event_loop()
            url = loop.run_until_complete(authorize((
                const.PLAYLIST_MODIFY_PUBLIC,
                const.PLAYLIST_MODIFY_PRIVATE,
                const.PLAYLIST_READ_COLLABORATIVE,
                const.PLAYLIST_READ_PRIVATE
            )))
            wx.CallAfter(self.open_auth_dialog, url=url)
        ## Error handling
        # usually a auth error
        elif status == RedirectListener.EVENT_SPOTIFY_ERROR:
            logger.console(f"Response from RedirectListener: Spotify Error {value.response_text}", "error")
            wx.CallAfter(self.frame.sbar.SetStatusText, value.response_text)
            wx.CallAfter(self.destroy_auth_dialog)
        elif status == RedirectListener.EVENT_SOCKET_ERROR:
            error_message = f"Response from RedirectListener: Socket Error, Check the debug.log for more details. {value.__str__()}"
            logger.console(error_message, "error")
            wx.CallAfter(self.frame.sbar.SetStatusText, error_message)
            wx.CallAfter(self.destroy_auth_dialog)
        

    def open_auth_dialog(self, url):
        self.auth_dialog = AuthDialog(self.frame, url)
        self.auth_dialog.ShowModal()
    
    def destroy_auth_dialog(self):
        self.auth_dialog.Destroy()
    
    def start_listening_for_redirect(self):
        """listen on the authorization redirect on port spotify.const.PORT
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
        """shows a standard error box

        Args:
            message (str): anything you like
        """
        # Create the message dialog
        dlg = wx.MessageDialog(self.frame, message, "Error", wx.OK | wx.ICON_ERROR)
        # Show the dialog and wait for the user to click "OK"
        dlg.ShowModal()
        # Destroy the dialog
        dlg.Destroy()



def add_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", 
        "--debug", 
        action="store_true", 
        default=False,
        help="enable debug mode")
    return parser.parse_args()

def run_app():

    # logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

    spotify_debug.DEBUG = add_args()
    if spotify_debug.DEBUG:
        # setup our spotify debugging if arguments are set to true
        spotify_debug.initialize()

    # create our logger APP
    logger.setup_logger()

    multiprocessing.freeze_support()
    spbackup_app = SPBackupApp()
    frame = MainFrame(app=spbackup_app, parent=None, title="Spotify Backup - coded by Paul Millar")
    frame.Show()
    spbackup_app.frame = frame
    spbackup_app.run_background_auth_check()
    spbackup_app.MainLoop()

if __name__ == '__main__':
    run_app()