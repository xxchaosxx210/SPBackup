import wx
import asyncio
import os
import multiprocessing

from main_frame import MainFrame
from auth_dialog import AuthDialog
from user_detail_dlg import show_user_info_dialog

import settings

from spotify.listener import RedirectListener
from spotify.net import authorize
from spotify.net import get_playlists
from spotify.net import get_user_info
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
        status, response = await get_playlists(self.token)
        if status == "ok":
            logger.info("Status returned OK")
            # Our response willl be the playlists json array
            wx.CallAfter(self.frame.main_panel.playlists_ctrl.populate, playlists=response)
            wx.CallAfter(self.frame.sbar.SetStatusText, text="Loaded Playlists successfully")
        else:
            wx.CallAfter(self.handle_spotify_error, response=response, function_name="get_playlists")
    
    async def retrieve_user_info(self):
        status, response = await get_user_info(self.token)
        if status == "ok":
            wx.CallAfter(show_user_info_dialog, parent=self.frame, userinfo=response)
        else:
            wx.CallAfter(self.handle_spotify_error, response=response, function_name="get_user_info")
    
    def handle_spotify_error(self, response, function_name):
        if response.status == 401:
            logger.error("Status returned 401")
            wx.CallAfter(self.frame.sbar.SetStatusText, 
            text=f'Error retrieving {function_name} with Status code: {response.status} and Reason: {response.reason}')
            settings.remove()
            self.start_listening_for_redirect()
        elif response.status == 403:
            self.show_error("403 Error, You do not have access to this request. Please logout and login again through your Spotify.")
            logger.error("Status returned 403")
            settings.remove()
        else:
            wx.CallAfter(
                self.frame.sbar.SetStatusText, 
                text=f'Error retrieving {function_name} with Status code: {response.status} and Reason: {response.reason}')
            logger.error(f"Status returned {response.status}, {response.reason}")
                
    
    def on_listener_response(self, status: str, value: any):
        if status == "token":
            # save the token to file
            settings.save(value)
            self.token = value
            wx.CallAfter(self.destroy_auth_dialog)
            wx.CallAfter(self.frame.sbar.SetStatusText, "Retrieving Playlists...")
            asyncio.run(self.retrieve_playlists())
        elif status == "authorize":
            url = authorize((
                const.PLAYLIST_MODIFY_PUBLIC,
                const.PLAYLIST_MODIFY_PRIVATE,
                const.PLAYLIST_READ_COLLABORATIVE,
                const.PLAYLIST_READ_PRIVATE
            ))
            wx.CallAfter(self.open_auth_dialog, url=url)
        elif status == "http-error":
            wx.CallAfter(self.frame.sbar.SetStatusText, 
            f'Error with Authentication. code: {value.status_code} and reason: {value.response.reason}')
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
                3000, 
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