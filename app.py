import wx
import asyncio

from main_frame import MainFrame
from auth_dialog import AuthDialog

import settings

from spotify.listener import RedirectListener
from spotify.net import authorize
from spotify.net import get_playlists
import spotify.const as const

class SPBackupApp(wx.App):

    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)
        self.frame = None

    def run_background_auth_check(self):
        self.token = settings.load()["token"]
        if not self.token:
            self.start_listening_for_redirect()
        else:
            asyncio.run(self.retrieve_playlists())
    
    async def retrieve_playlists(self):
        status, response = await get_playlists(self.token)
        if status == "ok":
            # Our response willl be the playlists json array
            wx.CallAfter(self.frame.main_panel.playlists_ctrl.populate, playlists=response)
        else:
            if response.status == 401:
                print(f'Error retrieving get_playlists with Status code: {response.status} and Reason: {response.reason}')
                print("...Removing token file")
                settings.remove()
                print("Please restart the App again")
            else:
                print(f'Error retrieving get_playlists with Status code: {response.status} and Reason: {response.reason}')
    
    def on_listener_response(self, status: str, value: any):
        if status == "token":
            # save the token to file
            settings.save(value)
            self.token = value
            wx.CallAfter(self.destroy_auth_dialog)
        elif status == "authorize":
            url = authorize((
                const.PLAYLIST_MODIFY_PUBLIC,
                const.PLAYLIST_MODIFY_PRIVATE,
                const.PLAYLIST_READ_COLLABORATIVE,
                const.PLAYLIST_READ_PRIVATE
            ))
            wx.CallAfter(self.open_auth_dialog, url=url)
        elif status == "http-error":
            print(f'Error with Authentication. code: {value.status_code} and reason: {value.response.reason}')
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



def run_app():
    spbackup_app = SPBackupApp()
    frame = MainFrame(None, title="Spotify Backup - coded by Paul Millar")
    frame.Show()
    spbackup_app.frame = frame
    spbackup_app.run_background_auth_check()
    spbackup_app.MainLoop()

if __name__ == '__main__':
    run_app()