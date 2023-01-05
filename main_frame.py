import wx

from playlists_ctrl import PlaylistsCtrl

class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        self.main_panel = MainPanel(self)

        self.sbar = self.CreateStatusBar()

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, 0)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizerAndFit(vbox)
        self.SetSize((640, 480))

class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.playlists_ctrl = PlaylistsCtrl(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.playlists_ctrl, 1, wx.ALL|wx.EXPAND, 0)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(vbox)
