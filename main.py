import wx
from spotify.listener import RedirectListener
from spotify.net import authorize
from spotify.net import get_playlists
import spotify.const as const
from spotify.serializers.playlist import Playlist
import app.utils as utils
from auth_dialog import AuthDialog
from playlists_ctrl import PlaylistsCtrl
import asyncio

class MainWindow(wx.Frame):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.main_panel = MainPanel(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, 0)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizerAndFit(vbox)
        self.SetSize((640, 480))
        self.token = utils.load()["token"]
        if not self.token:
            self.start_listening_for_redirect()
        else:
            asyncio.run(self.retrieve_playlists())
    
    async def retrieve_playlists(self):
        status, response = await get_playlists(self.token)
        if status == "ok":
            # Our response willl be the playlists json array
            wx.CallAfter(self.main_panel.playlists_ctrl.populate, playlists=response)
        else:
            if response.status == 401:
                print(f'Error retrieving get_playlists with Status code: {response.status} and Reason: {response.reason}')
                print("...Removing token file")
                utils.remove()
                print("Please restart the App again")
            else:
                print(f'Error retrieving get_playlists with Status code: {response.status} and Reason: {response.reason}')
    
    def on_listener_response(self, status: str, value: any):
        if status == "token":
            # save the token to file
            utils.save(value)
            self.token = value
            wx.CallAfter(self.destroy_auth_dialog)
        elif status == "authorize":
            url = authorize()
            wx.CallAfter(self.open_auth_dialog, url=url)
        elif status == "http-error":
            print(f'Error with Authentication. code: {value.status_code} and reason: {value.response.reason}')
            wx.CallAfter(self.destroy_auth_dialog)

    def open_auth_dialog(self, url):
        self.auth_dialog = AuthDialog(self, url)
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


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.playlists_ctrl = PlaylistsCtrl(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.playlists_ctrl, 1, wx.ALL|wx.EXPAND, 0)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)


def main():
    app = wx.App()
    frame = MainWindow(None, title="Spotify Backup - coded by Paul Millar")
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()