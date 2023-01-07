import wx
from ui.playlists_ctrl import PlaylistsCtrl
from ui.playlist_ctrl import PlaylistInfoCtrl

class PlaylistSplitterWindow(wx.SplitterWindow):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw, style=wx.SP_LIVE_UPDATE)

        self.playlists_ctrl = PlaylistsCtrl(self)
        self.playlistinfo_ctrl = PlaylistInfoCtrl(self)

        self.SplitHorizontally(self.playlists_ctrl, self.playlistinfo_ctrl)

        self.playlists_ctrl.SetMinSize((-1, 300))
        self.playlistinfo_ctrl.SetMinSize((-1, 100))

