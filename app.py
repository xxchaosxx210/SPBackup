import wx
import asyncio
import multiprocessing
import argparse

from ui.main_frame import MainFrame
from ui.dialogs.auth import AuthDialog
import ui.dialogs.user

import globals.config
import spotify.const
import spotify.net
import spotify.debug
from spotify.validators.playlists import Playlists as SpotifyPlaylists
from spotify.validators.playlist_info import PlaylistInfo as SpotifyPlaylistInfo
from spotify.validators.user import User as SpotifyUser
from spotify.validators.playlist_info import Tracks

from spotify.listener import RedirectListener

import playlist_manager

import globals.logger
from globals.state import (
    State,
    UI
)


class SPBackupApp(wx.App):

    def reset(self):
        """cleans up the UI and resets the global state for the Playlists
        """
        # Set the Playlists and PlayListInfo state to None
        State.set_playlist(None)
        State.set_playlists(None)
        # Disable the Buttons on the Toolbar
        UI.playlistinfo_toolbar.navbuttons.change_state()
        UI.playlists_toolbar.navbuttons.change_state()
        # Clear the ListCtrls
        UI.playlistinfo_ctrl.DeleteAllItems()
        UI.playlists_ctrl.DeleteAllItems()

    def reauthenticate(self):
        """restarts the authentication process again
        gets called when user presses the menuitem re-authenticate
        """
        self.reset()
        # remove the token
        globals.config.remove()
        # rerun the process of authentication
        self.run_background_auth_check()

    def run_background_auth_check(self):
        """this function loads the token if not found then new auth request started
        else will try and load users playlists and store the global token. 
        """
        # load the token from our .token.json file
        token: str = globals.config.load()["token"]
        State.set_token(token)
        if not token:
            globals.logger.console("No Token found. Requesting Authorization...", "info")
            self.start_listening_for_redirect()
        else:
            globals.logger.console("Token found. Retrieving Playlists from User...", "info")
            asyncio.run(self.retrieve_user_and_playlists(token))
    
    async def retrieve_user_and_playlists(self, token: str):
        await self.retrieve_playlists(token)
        user = await spotify.net.get_user_info(token)
        await State.playlist_manager.create_user(user)
    
    async def retrieve_playlists(self, token: str):
        """sends a get user playlist request and loads the Playlists listctrl if successful
        """
        try:
            playlists: SpotifyPlaylists = await spotify.net.get_playlists(token)
        except spotify.net.SpotifyError as err:
            self.handle_spotify_error(error=err)
            return
        State.set_playlists(playlists)
        wx.CallAfter(UI.playlists_ctrl.populate)
        wx.CallAfter(UI.statusbar.SetStatusText, text="Loaded Playlists successfully")
    
    async def retrieve_user_info(self):
        """sends a user information request and opens a dialog with user details
        """
        try:
            user: SpotifyUser = await spotify.net.get_user_info(State.get_token())
            # create a dialog with the User information
            wx.CallAfter(
                ui.dialogs.user.create_dialog, parent=UI.main_frame, userinfo=user)
        except spotify.net.SpotifyError as err:
            self.handle_spotify_error(error=err)
    
    async def retrieve_playlist(self, playlist_id: int):
        """sends a playlist request by ID. will set the global playlist if successful.
        Raises a SpotifyError if unsuccessful

        Args:
            playlist_id (int): the ID of the playlist too recieve
        """
        try:
            playlist: SpotifyPlaylistInfo = await spotify.net.get_playlist(State.get_token(), playlist_id)
            State.set_playlist(playlist)
            wx.CallAfter(
                UI.playlistinfo_ctrl.populate)
        except spotify.net.SpotifyError as err:
            State.set_playlist(None)
            self.handle_spotify_error(error=err)

    async def retrieve_tracks(self, url: str):
        """sends the next or previous link found in the PlaylistsInfo.Tracks object
        uodates the global tracks state and loads the PlaylistInfoCtrl with the tracks

        Args:
            url (str): the url to follow. found in State.playlistinfo.tracks
        """
        try:
            tracks: Tracks = await spotify.net.get_tracks_from_url(State.get_token(), url)
            State.update_playlist_tracks(tracks)
            wx.CallAfter(UI.playlistinfo_ctrl.populate)
        except spotify.net.SpotifyError as err:
            self.handle_spotify_error(error=err)

    async def retrieve_playlist_items(self, url: str):
        """requests for the next or previous url found in the playlists.next or playlists.previous properties.
        called when the User presses on the next or previous button. For pagination if more usbers playlists exceed spotify maximum limit

        Args:
            url (str): the url to follow next
        """
        try:
            playlists: SpotifyPlaylists = await spotify.net.get_playlists(token=State.get_token(), url=url)
        except spotify.net.SpotifyError as err:
            self.handle_spotify_error(error=err)
        State.set_playlists(playlists)
        wx.CallAfter(UI.playlists_ctrl.populate)
    
    def handle_spotify_error(self, error: spotify.net.SpotifyError):
        """handle the error status codes recieved from Spotify

        Args:
            error (SpotifyError): exceptioon object
        """
        if error.code == spotify.const.STATUS_BAD_TOKEN:
            # bad token ask for a re-authorize request from the user
            wx.CallAfter(UI.statusbar.SetStatusText, text=error.response_text)
            globals.config.remove()
            self.start_listening_for_redirect()
        elif error.code == spotify.const.STATUS_BAD_OAUTH_REQUEST:
            self.show_error(error.response_text)
            globals.config.remove()
        else:
            wx.CallAfter(UI.statusbar.SetStatusText, text=error.response_text)  
    
    def on_listener_response(self, status: int, value: any):
        """response from the RedirectListener

        Args:
            status (str): read the RedirectListener EVENT for documentation
            value (any): depends on status. If an error then it will be error object else json
        """
        if status == RedirectListener.EVENT_TOKEN_RECIEVED:
            # We have authentication save the token and use until 401 error again and restart this process again to obtain another token
            # save the token to file
            globals.config.save(value)
            State.set_token(value)
            globals.logger.console("Response from RedirectListener: Token recieved and saved", "info")
            wx.CallAfter(self.destroy_auth_dialog)
            wx.CallAfter(UI.statusbar.SetStatusText, "Retrieving Playlists...")
            asyncio.run(self.retrieve_user_and_playlists(value))
        elif status == RedirectListener.EVENT_AUTHORIZATION_ERROR:
            # There was an issue with the Authorization response and HTTP parsing
            State.set_token(None)
            globals.config.remove()
            wx.CallAfter(self.destroy_auth_dialog)
            globals.logger.console(value, "error")
        elif status == RedirectListener.EVENT_REQUESTING_AUTHORIZATION:
            # We need a new token. create a new playlist scope and request from Spotify a new Token
            # Prompt user to follow Url
            globals.logger.console("Response from RedirectListener: Requesting Authorization...", "info")
            loop = asyncio.new_event_loop()
            url = loop.run_until_complete(spotify.net.authorize((
                spotify.const.PLAYLIST_MODIFY_PUBLIC,
                spotify.const.PLAYLIST_MODIFY_PRIVATE,
                spotify.const.PLAYLIST_READ_COLLABORATIVE,
                spotify.const.PLAYLIST_READ_PRIVATE
            )))
            wx.CallAfter(self.open_auth_dialog, url=url)
        ## Error handling
        # usually a auth error
        elif status == RedirectListener.EVENT_SPOTIFY_ERROR:
            globals.logger.console(f"Response from RedirectListener: Spotify Error {value.response_text}", "error")
            wx.CallAfter(UI.statusbar.SetStatusText, value.response_text)
            wx.CallAfter(self.destroy_auth_dialog)
        elif status == RedirectListener.EVENT_SOCKET_ERROR:
            error_message = f"Response from RedirectListener: Socket Error, Check the debug.log for more details. {value.__str__()}"
            globals.logger.console(error_message, "error")
            wx.CallAfter(UI.statusbar.SetStatusText, error_message)
            wx.CallAfter(self.destroy_auth_dialog)
        
    def open_auth_dialog(self, url):
        self.auth_dialog = AuthDialog(UI.main_frame, url)
        self.auth_dialog.ShowModal()
    
    def destroy_auth_dialog(self):
        self.auth_dialog.Destroy()
    
    def start_listening_for_redirect(self):
        """
        sets up the RedirectListener thread. Sends a authorization request to Spotify
        sets up a socket and listens for reply to the auth url to follow which is prompted to the user
        once the user clicks authorize then the server will close and send a token to the self.on_listener_response
        check the spotify.listener for more details
        """
        if not hasattr(self, "listener") or not self.listener.is_alive():
            self.listener = RedirectListener(
                globals.config.APP_NAME, self.on_listener_response)
            self.listener.start()
    
    def show_error(self, message: str):
        """shows a standard error box

        Args:
            message (str): anything you like
        """
        # Create the message dialog
        dlg = wx.MessageDialog(UI.main_frame, message, "Error", wx.OK | wx.ICON_ERROR)
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

    spotify.debugging.DEBUG = add_args()
    if spotify.debugging.DEBUG:
        # setup our spotify debugging if arguments are set to true
        spotify.debugging.initialize()

    # create our logger APP
    globals.logger.setup_logger()

    State.playlist_manager = playlist_manager.PlaylistManager()

    multiprocessing.freeze_support()
    app = SPBackupApp()
    UI.main_frame = MainFrame(
        app=app, 
        parent=None, 
        title=f"{globals.config.APP_NAME} v{globals.config.APP_VERSION} - coded by {globals.config.APP_AUTHOR}")
    UI.main_frame.Show()
    app.run_background_auth_check()
    app.MainLoop()

if __name__ == '__main__':
    run_app()