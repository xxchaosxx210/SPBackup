import wx
import wx.lib.mixins.listctrl as listmix
from spotify.serializers.playlist_info import PlaylistInfo
from spotify.serializers.playlist_info import Artist
from spotify.serializers.playlist_info import Item

from globals.state import State
import globals.logger as logger


class PlaylistInfoToolBar(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)

        # Create a horizontal box sizer
        h_box = wx.BoxSizer(wx.HORIZONTAL)

        # Create a vertical box sizer
        v_box = wx.BoxSizer(wx.VERTICAL)

        # Add the horizontal box sizer to the vertical box sizer
        v_box.Add(h_box, 1, wx.EXPAND)

        # Create the "prev" button and bind the event handler
        prev_btn = wx.Button(self, label="prev")
        self.Bind(wx.EVT_BUTTON, self.on_prev, prev_btn)
        # Add the button to the horizontal box sizer
        h_box.Add(prev_btn, 0, wx.ALL, 5)

        # Create the "next" button and bind the event handler
        next_btn = wx.Button(self, label="next")
        self.Bind(wx.EVT_BUTTON, self.on_next, next_btn)
        # Add the button to the horizontal box sizer
        h_box.Add(next_btn, 0, wx.ALL, 5)

        # Set the sizer for the panel
        self.SetSizer(v_box)

    def on_prev(self, event):
        # Handle the "prev" button press here
        playlist = State.get_playlist()
        if playlist:
            logger.console(f'Previous page link is: {playlist.tracks.next}')

    def on_next(self, event):
        # Handle the "next" button press here
        playlist = State.get_playlist()
        if playlist:
            logger.console(f'Next page link is: {playlist.tracks.next}')


class PlaylistInfoCtrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
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
        
        self.SetColumnWidth(0, 50)
        self.SetColumnWidth(1, 300)
        self.SetColumnWidth(2, 200)
        self.SetColumnWidth(3, 200)
        self.SetColumnWidth(4, 100)

        self.SetMinSize((100, 200))
        self.setResizeColumn(2)
        self.SetAutoLayout(True)
    
    def populate(self, playlist: PlaylistInfo):
        self.clear_items()
        State.set_playlist(playlist)
        for item_index, item in enumerate(playlist.tracks.items):
            self.add_item(item_index, item)

    def clear_items(self):
        self.DeleteAllItems()
        State.set_playlist(None)
    
    def add_item(self, item_index: int, item: Item):
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