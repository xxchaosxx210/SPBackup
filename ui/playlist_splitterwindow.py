import wx
from ui.playlistsctrl import PlaylistsCtrl
from ui.tracksctrl import TracksCtrl
from globals.state import UI


class PlaylistSplitterWindow(wx.SplitterWindow):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw, style=wx.SP_LIVE_UPDATE)

        UI.playlists_ctrl = PlaylistsCtrl(self)
        UI.tracksctrl = TracksCtrl(self)

        self.SplitHorizontally(UI.playlists_ctrl, UI.tracksctrl)

        UI.playlists_ctrl.SetMinSize((-1, -1))
        UI.tracksctrl.SetMinSize((-1, -1))

