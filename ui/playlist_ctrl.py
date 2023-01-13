import wx
import asyncio
import wx.lib.mixins.listctrl as listmix
from spotify.validators.playlist_info import Artist
from spotify.validators.playlist_info import Item
from ui.navbuttonpanel import NavButtonPanel

from globals.state import (
    State,
    UI
)

class PlaylistInfoNavButtonPanel(NavButtonPanel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.backup_button.SetToolTip("Backup Tracks from this Playlist")
        self.restore_button.SetToolTip("Restore Tracks to this Playlist")

    def change_state(self):
        playlist = State.get_playlist()
        self.next_button.Disable() if not playlist or not playlist.tracks or not playlist.tracks.next \
            else self.next_button.Enable(True)
        self.prev_button.Disable() if not playlist or not playlist.tracks or not playlist.tracks.previous \
            else self.prev_button.Enable(True)

    def on_prev_button(self, event: wx.CommandEvent):
        # Handle the "prev" button press here
        playlist = State.get_playlist()
        if playlist:
            if playlist.tracks.previous is not None:
                app = wx.GetApp()
                asyncio.run(app.retrieve_tracks(playlist.tracks.previous))

    def on_next_button(self, event: wx.CommandEvent):
        # Handle the "next" button press here
        playlist = State.get_playlist()
        if playlist:
            if playlist.tracks.next is not None:
                app = wx.GetApp()
                asyncio.get_event_loop().create_task(
                    app.retrieve_tracks(playlist.tracks.next))

    def on_backup_click(self, evt: wx.CommandEvent):
        print("Backup clicked")
    
    def on_restore_click(self, evt: wx.CommandEvent):
        print("Restore clicked")
        
class PlaylistInfoToolBar(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        self.navbuttons = PlaylistInfoNavButtonPanel(self)

        h_box: wx.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        h_box.Add(self.navbuttons, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        v_box = wx.BoxSizer(wx.VERTICAL)
        v_box.Add(h_box, 1, wx.ALIGN_CENTER)
        self.SetSizer(v_box)


class PlaylistInfoCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.EnableCheckBoxes(True)

        columns = (
            "Select",
            "#",
            "Song",
            "Artist",
            "Album",
            "Date Added"
        )

        for index, column in enumerate(columns):
            self.InsertColumn(index, column)
        
        self.SetColumnWidth(0, 50)
        self.SetColumnWidth(1, 50)
        self.SetColumnWidth(2, 300)
        self.SetColumnWidth(3, 200)
        self.SetColumnWidth(4, 200)
        self.SetColumnWidth(5, 100)

        self.SetMinSize((100, 200))
        self.setResizeColumn(2)
        self.SetAutoLayout(True)
    
    def populate(self):
        playlist = State.get_playlist()
        self.clear_items()
        UI.playlistinfo_toolbar.navbuttons.change_state()
        for item_index, item in enumerate(playlist.tracks.items):
            self.add_item(item_index, item)

    def clear_items(self):
        self.DeleteAllItems()
    
    def add_item(self, item_index: int, item: Item):
        row_index = self.InsertItem(index=item_index, label="")
        select_item: wx.ListItem = self.GetItem(row_index, 0)
        select_item.SetState(wx.LIST_STATE_SELECTED)
        def get_artist_name(_artist: Artist) -> str:
            """extract the name of the artists. Should be used in a map iteration function to iterate through the artists collaboration

            Args:
                _artist (Artist): the artist from the item

            Returns:
                str: the name of the artist
            """
            return _artist.name
        # Append artists
        offset_index = State.get_playlist().tracks.offset + item_index + 1
        self.SetItem(row_index, 1, str(offset_index))
        self.SetItem(row_index, 2, item.track_name)
        artist_string = " / ".join(map(get_artist_name, item.track_album.artists))
        self.SetItem(row_index, 3, artist_string)
        self.SetItem(row_index, 4, item.track_album.name)
        self.SetItem(row_index, 5, item.added_at)