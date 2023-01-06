import wx
import wx.lib.mixins.listctrl as listmix
from spotify.serializers.playlist import Playlist


class PlaylistsCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        listmix.ListCtrlAutoWidthMixin.__init__(self)