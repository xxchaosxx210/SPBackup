import wx
import wx.lib.mixins.listctrl as listmix
from spotify.serializers.playlist_info import Playlist
from spotify.serializers.playlist_info import Track
from spotify.serializers.playlist_info import Item


class TrackListCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        columns = (
            "#",
            "Song",
            "Artist",
            "Album",
            "Date Added"
        )

        for index, column in enumerate(columns):
            self.InsertColumn(index, column)
            # if column == "#":
            #     self.SetColumnWidth(index, 30)
        
        self.SetColumnWidth(0, 20)
        self.SetColumnWidth(1, 300)
        self.SetColumnWidth(2, 200)
        self.SetColumnWidth(3, 200)
        self.SetColumnWidth(4, 100)

        self._items = []

        self.SetMinSize((100, 200))
        self.setResizeColumn(2)
        self.SetAutoLayout(True)
    
    def populate(self, playlist: Playlist):
        self.clear_items()
        for index, item in enumerate(playlist.tracks.items):
            self.add_item(index, item)

    def clear_items(self):
        self.DeleteAllItems()
        self._items = []
    
    def add_item(self, index: int, item: Item):
        self._items.append(item)  # Add the Playlist object to the list

        self.InsertItem(index, str(index+1), index)
        def get_artist_name(_artist):
            return _artist.name
        # Append artists
        self.SetItem(index, 1, item.track.name)
        artist_string = " / ".join(map(get_artist_name, item.track.album.artists))
        self.SetItem(index, 2, artist_string)
        self.SetItem(index, 3, item.track.album.name)
        self.SetItem(index, 4, item.added_at)