import wx
import wx.lib.mixins.listctrl as listmix
from spotify.serializers.playlist_info import PlaylistInfo
from spotify.serializers.playlist_info import Artist
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
        
        self.SetColumnWidth(0, 50)
        self.SetColumnWidth(1, 300)
        self.SetColumnWidth(2, 200)
        self.SetColumnWidth(3, 200)
        self.SetColumnWidth(4, 100)

        self._items = []

        self.SetMinSize((100, 200))
        self.setResizeColumn(2)
        self.SetAutoLayout(True)
    
    def populate(self, playlist: PlaylistInfo):
        self.clear_items()
        for item_index, item in enumerate(playlist.tracks.items):
            self.add_item(item_index, item)

    def clear_items(self):
        self.DeleteAllItems()
        self._items = []
    
    def add_item(self, item_index: int, item: Item):
        self._items.append(item)  # Add the PlaylistInfo object to the list
        row_index = self.InsertItem(index=item_index, label=str(item_index+1))
        def get_artist_name(_artist: Artist) -> str:
            """extract the name of the artists. Should be used in a map iteration function to iterate through the artists collaboration

            Args:
                _artist (Artist): the artist from the item

            Returns:
                str: the name of the artist
            """
            return _artist.name
        # Append artists
        self.SetItem(row_index, 1, item.track_name)
        artist_string = " / ".join(map(get_artist_name, item.track_album.artists))
        self.SetItem(row_index, 2, artist_string)
        self.SetItem(row_index, 3, item.track_album.name)
        self.SetItem(row_index, 4, item.added_at)