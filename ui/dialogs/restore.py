import wx


class BackupsListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the columns
        self.InsertColumn(0, "Date", width=100)
        self.InsertColumn(1, "Name", width=100)
        self.InsertColumn(2, "Description", width=200)

    def OnSize(self, event):
        width = self.GetSize().width
        self.SetColumnWidth(0, width/5)
        self.SetColumnWidth(1, width/5)
        self.SetColumnWidth(2, 3*width/5)
        event.Skip()


class RestorePanel(wx.Panel):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetBackgroundColour(wx.GREEN)
        self.restore_lisctrl = BackupsListCtrl(parent=self, style=wx.LC_REPORT)
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.RED)
        gbs = wx.GridBagSizer()
        gbs.Add(self.restore_lisctrl, pos=(0, 0), flag=wx.EXPAND | wx.ALL)
        gbs.Add(self.panel, pos=(1, 0), flag=wx.EXPAND | wx.ALL)
        gbs.AddGrowableCol(0, 1)
        gbs.AddGrowableRow(0, 1)
        self.SetSizerAndFit(gbs)


class RestoreDialog(wx.Dialog):

    def __init__(self, parent):
        super().__init__(parent=parent, title="Restore Backup",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.panel = RestorePanel(parent=self)
        gs = wx.GridSizer(cols=1)
        gs.Add(self.panel, proportion=1, flag=wx.ALL | wx.EXPAND)
        self.SetSizerAndFit(gs)
        self.SetSize((800, 600))
        self.CenterOnParent()
