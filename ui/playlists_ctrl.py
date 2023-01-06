import wx
from spotify.serializers.playlist import Playlist

class PlaylistsCtrl(wx.ListCtrl):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)

        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Description")
        self.InsertColumn(2, "Created by")
        self.InsertColumn(3, "ID")
        self.InsertColumn(4, "Tracks amount")

        self._playlists = []

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

    def populate(self, playlists):
        # Clear the list control
        self.clear_playlists()

        # Add the playlists to the list control
        for playlist in playlists:
            self.add_playlist(Playlist(**playlist))
    
    def clear_playlists(self):
        self.DeleteAllItems()
        self._playlists = []
    
    def add_playlist(self, playlist: Playlist):
        index = len(self._playlists)  # Get the next available index ID
        self._playlists.append(playlist)  # Add the Playlist object to the list

        self.InsertItem(index, playlist.name, index)
        self.SetItem(index, 1, playlist.description)
        self.SetItem(index, 2, playlist.owner.display_name)
        self.SetItem(index, 3, str(playlist.id))
        self.SetItem(index, 4, str(playlist.tracks.total))

    def OnItemSelected(self, event):
        item_index = event.GetIndex()
        playlist_index = self.GetItemData(item_index)
        # Do something with the Playlist object
        print("Selected item:", item_index)
        print("Associated Playlist:", self._playlists[playlist_index])
