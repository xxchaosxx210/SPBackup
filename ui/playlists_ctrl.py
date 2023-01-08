import wx
import asyncio
import wx.lib.mixins.listctrl as listmix
from spotify.serializers.playlists import Item as PlaylistsItem
from globals.state import (
    State,
    UI
)

class PlaylistsToolBar(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        # Create a horizontal box sizer
        h_box = wx.BoxSizer(wx.HORIZONTAL)

        # Create a vertical box sizer
        v_box = wx.BoxSizer(wx.VERTICAL)

        # Add the horizontal box sizer to the vertical box sizer
        v_box.Add(h_box, 1, wx.EXPAND)

        # Create the "prev" button and bind the event handler
        self.prev_btn = wx.Button(self, label="prev")
        self.prev_btn.Disable()  # disable the button
        self.Bind(wx.EVT_BUTTON, self.on_prev, self.prev_btn)
        # Add the button to the horizontal box sizer
        h_box.Add(self.prev_btn, 0, wx.ALL, 5)

        # Create the "next" button and bind the event handler
        self.next_btn = wx.Button(self, label="next")
        self.next_btn.Disable()  # disable the button
        self.Bind(wx.EVT_BUTTON, self.on_next, self.next_btn)
        # Add the button to the horizontal box sizer
        h_box.Add(self.next_btn, 0, wx.ALL, 5)

        # Set the sizer for the panel
        self.SetSizer(v_box)

    def change_nav_button_state(self):
        playlists = State.get_playlists()
        self.next_btn.Disable() if not playlists or not playlists.next else self.next_btn.Enable(True)
        self.prev_btn.Disable() if not playlists or not playlists.previous else self.prev_btn.Enable(True)

    def on_prev(self, _):
        # Handle the "prev" button press here
        playlists = State.get_playlists()
        if not playlists or not playlists.previous:
            return
        app = wx.GetApp()
        asyncio.run(app.retrieve_playlist_items(playlists.previous))
        # logger.console(f'Previous page link is: {playlists.previous}')

    def on_next(self, _):
        # Handle the "next" button press here
        playlists = State.get_playlists()
        if not playlists or not playlists.next:
            return
        app = wx.GetApp()
        asyncio.run(app.retrieve_playlist_items(playlists.next))
        # logger.console(f'Next page link is: {playlists.next}')


class PlaylistsCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Description")
        self.InsertColumn(2, "Created by")
        self.InsertColumn(3, "ID")
        self.InsertColumn(4, "Tracks amount")
        
        # Set the minimum size of the widget
        self.SetMinSize((100, 200))

        self.SetColumnWidth(0, 200)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, 100)
        self.SetColumnWidth(4, 100)

        self.setResizeColumn(2)

        self.SetAutoLayout(True)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)

    def populate(self):
        # Clear the list control
        self.clear_playlists()
        # Add the playlists to the list control
        playlists = State.get_playlists()
        UI.playlists_toolbar.change_nav_button_state()
        for index, playlist in enumerate(playlists.items):
            self.add_playlist(index, playlist)
    
    def clear_playlists(self):
        self.DeleteAllItems()
    
    def add_playlist(self, index, playlist: PlaylistsItem):
        self.InsertItem(index, playlist.name, index)
        self.SetItem(index, 1, playlist.description)
        self.SetItem(index, 2, playlist.owner.display_name)
        self.SetItem(index, 3, str(playlist.id))
        self.SetItem(index, 4, str(playlist.tracks.total))

    def OnItemSelected(self, event):
        item_index = event.GetIndex()
        # Do something with the Playlist object
        app = wx.GetApp()
        playlist: PlaylistsItem = State.get_playlists().items[item_index]
        asyncio.run(app.retrieve_playlist(playlist.id))