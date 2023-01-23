from typing import (
    List,
)

import wx

import database


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

    def populate(self, backups: List[database.Backup]):
        for index, backup in enumerate(backups):
            # self.InsertStringItem(backup.id, backup.date_added.strftime('%d-%m-%Y %H:%M:%S'))
            # self.SetStringItem(backup.id, 1, backup.name)
            # self.SetStringItem(backup.id, 2, backup.description)
            self.add_backup(index, backup)

    def add_backup(self, index: int, backup: database.Backup) -> None:
        self.InsertItem(index, label=backup.date_added)
        self.SetItem(index, 1, label=backup.name)
        self.SetItem(index, 2, label=backup.description)


class RestorePanel(wx.Panel):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.restore_lisctrl = BackupsListCtrl(parent=self, style=wx.LC_REPORT)
        gbs = wx.GridBagSizer()
        gbs.Add(self.restore_lisctrl, pos=(0, 0), flag=wx.EXPAND | wx.ALL)
        gbs.AddGrowableCol(0, 1)
        gbs.AddGrowableRow(0, 1)
        self.SetSizerAndFit(gbs)


class ButtonPanel(wx.Panel):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        restore_btn = wx.Button(parent=self, id=wx.ID_OK, label="Restore")
        cancel_btn = wx.Button(parent=self, id=wx.ID_CANCEL, label="Cancel")
        gs = wx.GridSizer(1, 2, 0, 0)
        gs.Add(restore_btn, 0)
        gs.Add(cancel_btn, 0)
        self.SetSizerAndFit(gs)


class RestoreDialog(wx.Dialog):

    def __init__(self, parent):
        super().__init__(parent=parent, title="Restore Backup",
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.main_panel = RestorePanel(parent=self)
        self.button_panel = ButtonPanel(parent=self)
        gs = wx.GridBagSizer()
        gs.Add(self.main_panel, pos=(0, 0), flag=wx.ALL | wx.EXPAND | wx.BOTH)
        gs.Add(self.button_panel, pos=(1, 0), flag=wx.ALIGN_CENTER_HORIZONTAL)
        gs.AddGrowableCol(0, 1)
        gs.AddGrowableRow(0, 1)
        self.SetSizerAndFit(gs)
        self.SetSize((800, 600))
        self.CenterOnParent()

        self.Bind(wx.EVT_INIT_DIALOG, self.on_init)

    def on_init(self, evt: wx.CommandEvent):
        # load the backups
        pass

    def on_database_event():
        pass
