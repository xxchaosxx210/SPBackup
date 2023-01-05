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

    def populate(self, playlists):
        # Clear the list control
        self.DeleteAllItems()

        # Add the playlists to the list control
        for playlist in playlists:
            plst = Playlist(**playlist)
            self.Append((
              plst.name  , plst.description, plst.owner.display_name, plst.id, str(plst.tracks.total)
            ))