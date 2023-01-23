from typing import (
    List,
)
import asyncio

import wx
import wxasync

import database
import globals


class PaginatePanel(wx.Panel):

    def __init__(self, title: str, columns: List[dict], *args, **kw):
        super().__init__(*args, **kw)

        staticbox = wx.StaticBox(self, label=title)
        static_sizer = wx.StaticBoxSizer(staticbox, wx.VERTICAL)

        self.listctrl = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.create_columns(columns)

        self.prev_button = wx.Button(self, label="Prev")
        self.next_button = wx.Button(self, label="Next")

        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(self.prev_button, proportion=0)
        button_sizer.Add(self.next_button, proportion=0)

        static_sizer.Add(self.listctrl, 1, flag=wx.EXPAND | wx.ALL)
        static_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER)

        self.SetSizerAndFit(static_sizer)

    def create_columns(self, columns: List[dict]):
        for index, column in enumerate(columns):
            self.listctrl.InsertColumn(
                index, column["label"], width=column["width"])

    def populate(self, objects: List[any]):
        pass


class BackupsListPanel(PaginatePanel):

    def __init__(self, *args, **kw):
        columns = [
            {
                "label": "Date Added",
                "width": 100
            },
            {
                "label": "Name",
                "width": 100
            },
            {
                "label": "Description",
                "width": 300
            }
        ]
        super().__init__(title="Backups", columns=columns, *args, **kw)

    def populate(self, objects: List[any]):
        return super().populate(objects)

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
        self.backups_listpanel = BackupsListPanel(parent=self)
        gbs = wx.GridBagSizer()
        gbs.Add(self.backups_listpanel, pos=(0, 0), flag=wx.EXPAND | wx.ALL)
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

    get_backup_task: asyncio.Task = None
    instance: wx.Dialog = None

    def __init__(self, parent: wx.Window):
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

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_SHOW, self.on_show)

    def on_close(self, evt: wx.CommandEvent):
        task = RestoreDialog.get_backup_task
        if task is not None and not task.done():
            task.cancel()

    def on_show(self, evt: wx.CommandEvent):
        # load the backups
        dlg: RestoreDialog = evt.GetEventObject()
        if not dlg.IsShown():
            RestoreDialog.get_backup_task = asyncio.create_task(
                self.load_backups())

    async def load_backups(self):
        # app = wx.GetApp()
        # local_db: database.LocalDatabase = app.playlist_manager.local_db
        # genfunc = await local_db.iter_backups(0, 1000)
        # pass
        globals.logger.console("Shown window")


def load_dialog(parent: wx.Window):
    if RestoreDialog.instance is not None and RestoreDialog.instance.IsShown():
        return
    RestoreDialog.instance = RestoreDialog(parent=parent)