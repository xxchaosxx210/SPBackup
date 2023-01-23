import wx
import asyncio

import wx.lib.mixins.listctrl as listmix

from spotify.validators.playlists import Item as PlaylistsItem
from globals.state import (
    SpotifyState,
    UI,
    UserState
)
from ui.navbuttonpanel import NavButtonPanel
import ui.dialogs.restore


class PlaylistsNavButtonsPanel(NavButtonPanel):
    def __init__(self, parent):
        super().__init__(parent)

        self.backup_button.SetToolTip("Backup Playlists")
        self.restore_button.SetToolTip("Restore Playlists")

    def change_state(self):
        playlists = SpotifyState.get_playlists()
        self.next_button.Disable() if not playlists or not playlists.next else self.next_button.Enable(
            True
        )
        self.prev_button.Disable() if not playlists or not playlists.previous else self.prev_button.Enable(
            True
        )

    def on_prev_button(self, event: wx.CommandEvent):
        playlists = SpotifyState.get_playlists()
        if not playlists or not playlists.previous:
            return
        app = wx.GetApp()
        asyncio.get_event_loop().create_task(
            app.retrieve_playlist_items(playlists.previous)
        )

    def on_next_button(self, event: wx.CommandEvent):
        playlists = SpotifyState.get_playlists()
        if not playlists or not playlists.next:
            return
        app = wx.GetApp()
        asyncio.get_event_loop().create_task(
            app.retrieve_playlist_items(playlists.next)
        )

    def on_backup_click(self, evt: wx.CommandEvent):
        app: wx.App = wx.GetApp()
        token = UserState.get_token()
        task: asyncio.Task = app.playlist_manager.running_task
        if not token or task and not (task.done() or task.cancelled()):
            # bad token or task is running ignore the button press
            return
        app.playlist_manager.running_task = asyncio.create_task(
            app.playlist_manager.backup_playlists(
                token, app.playlists_backup_handler, "Test", "This is a test purpose entry only"))

    def on_restore_click(self, evt: wx.CommandEvent):
        ui.dialogs.restore.load_dialog(UI.main_frame)


class PlaylistsToolBar(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.navbuttons = PlaylistsNavButtonsPanel(self)
        h_box: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        h_box.Add(self.navbuttons, 0, wx.ALL | wx.ALIGN_CENTER, 0)
        v_box = wx.BoxSizer(wx.VERTICAL)
        v_box.Add(h_box, 1, wx.ALIGN_CENTER)
        self.SetSizer(v_box)


class PlaylistsCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.EnableCheckBoxes(True)

        self.InsertColumn(0, "Select")
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "Description")
        self.InsertColumn(3, "Created by")
        self.InsertColumn(4, "ID")
        self.InsertColumn(5, "Tracks amount")

        # Set the minimum size of the widget
        self.SetMinSize((100, 200))

        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 200)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(4, 100)
        self.SetColumnWidth(5, 100)

        self.setResizeColumn(2)

        self.SetAutoLayout(True)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

    def populate(self, playlists: PlaylistsItem):
        # Clear the list control
        self.clear_playlists()
        # Add the playlists to the list control
        UI.playlists_toolbar.navbuttons.change_state()
        for index, playlist in enumerate(playlists):
            self.add_playlist(index, playlist)

    def clear_playlists(self):
        self.DeleteAllItems()

    def add_playlist(self, index, playlist: PlaylistsItem):
        self.InsertItem(index, "", index)
        item: wx.ListItem = self.GetItem(index, 0)
        item.SetState(wx.LIST_STATE_SELECTED)
        # self.SetItemState(index, wx.LIST_STATE_CHECKED, wx.LIST_STATE_CHECKED)
        self.SetItem(index, 1, playlist.name)
        self.SetItem(index, 2, playlist.description)
        self.SetItem(index, 3, playlist.owner.display_name)
        self.SetItem(index, 4, str(playlist.id))
        self.SetItem(index, 5, str(playlist.tracks.total))

    def OnItemSelected(self, event):
        item_index = event.GetIndex()
        app = wx.GetApp()
        playlist: PlaylistsItem = SpotifyState.get_playlists(
        ).items[item_index]
        loop = asyncio.get_event_loop()
        loop.create_task(app.retrieve_playlist(playlist.id))
