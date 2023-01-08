import wx
from ui.playlists_ctrl import PlaylistsCtrl
from ui.playlist_ctrl import PlaylistInfoCtrl
from globals.state import UI


class PlaylistSplitterWindow(wx.SplitterWindow):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw, style=wx.SP_LIVE_UPDATE)

        UI.playlists_ctrl = PlaylistsCtrl(self)
        UI.playlistinfo_ctrl = PlaylistInfoCtrl(self)

        self.SplitHorizontally(UI.playlists_ctrl, UI.playlistinfo_ctrl)

        UI.playlists_ctrl.SetMinSize((-1, 300))
        UI.playlistinfo_ctrl.SetMinSize((-1, 100))

