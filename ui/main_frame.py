import wx
import asyncio

from ui.playlist_splitterwindow import PlaylistSplitterWindow
from ui.playlist_ctrl import PlaylistInfoToolBar
from ui.playlists_ctrl import PlaylistsToolBar
from globals.state import UI
from globals.state import State
import globals.logger
from spotify.validators.playlist import Playlist
from spotify.validators.tracks import Tracks
from spotify.validators.tracks import Track
import spotify.net
import image_manager

from ui.dialogs.bubbledialog import BubbleDialog
from ui.dialogs.loading import LoadingDialog

class MainFrame(wx.Frame):

    def __init__(self, app=None, *args, **kw):
        super().__init__(*args, **kw)

        self.app = app

        self.SetIcon(wx.Icon(image_manager.ICON_PATH))

        self.main_panel = MainPanel(self)

        UI.statusbar = self.CreateStatusBar()

        self.create_menubar()

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, 0)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizerAndFit(vbox)
        self.SetSize((600, 600))


    def create_menubar(self):
        """Creates the menu bar."""
        # Create a menu bar
        self.menu_bar = wx.MenuBar()

        # Create a User menu
        self.user_menu = wx.Menu()

        # Create a Details menu item
        self.details_item = wx.MenuItem(self.user_menu, wx.ID_ANY, "Details")
        self.user_menu.Append(self.details_item)
        self.Bind(wx.EVT_MENU, self.on_details, self.details_item)

        # Create a Re-authorize menu item
        self.reauth_item = wx.MenuItem(self.user_menu, wx.ID_ANY, "Re-authorize")
        self.user_menu.Append(self.reauth_item)
        self.Bind(wx.EVT_MENU, self.on_reauth, self.reauth_item)

        # Add the User menu to the menu bar
        self.menu_bar.Append(self.user_menu, "User")

        # View Menu creation
        self.view_menu = wx.Menu()

        # Create a Hide Playlists MenuItem
        self.hide_playlists_menuitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, "Hide Playlists", kind=wx.ITEM_CHECK)
        self.Bind(
            wx.EVT_MENU, self.toggle_hide_playlists, self.hide_playlists_menuitem)
        self.view_menu.Append(self.hide_playlists_menuitem)
        # Create a Hide Tracks MenuItem
        self.hide_tracks_menuitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, "Hide Tracks", kind=wx.ITEM_CHECK)
        self.Bind(
            wx.EVT_MENU, self.toggle_hide_tracks, self.hide_tracks_menuitem)
        self.view_menu.Append(self.hide_tracks_menuitem)

        self.menu_bar.Append(self.view_menu, "View")

        self.debug_menu = wx.Menu()
        self.all_tracks = wx.MenuItem(self.debug_menu, wx.ID_ANY, "Get All Tracks")
        self.Bind(wx.EVT_MENU, self.on_get_all_tracks, self.all_tracks)
        self.debug_menu.Append(self.all_tracks)

        show_loading_dlg = wx.MenuItem(self.debug_menu, wx.ID_ANY, "Show Loading Dialog")
        self.Bind(wx.EVT_MENU, self.on_show_loading_dlg, show_loading_dlg)
        self.debug_menu.Append(show_loading_dlg)

        self.menu_bar.Append(self.debug_menu, "Debug")

        self.help_menu = wx.Menu()
        self.about_menuitem = wx.MenuItem(self.help_menu, wx.ID_ANY, "About")
        self.Bind(wx.EVT_MENU, self.on_about_menu, self.about_menuitem)
        self.help_menu.Append(self.about_menuitem)

        self.menu_bar.Append(self.help_menu, "Help")

        # Set the frame's menu bar
        self.SetMenuBar(self.menu_bar)
        
    def on_get_all_tracks(self, evt: wx.CommandEvent):
        index = UI.playlists_ctrl.GetFirstSelected()
        if index == -1:
            return
        playlist: Playlist = State.get_playlists().items[index]
        loop = spotify.net.get_event_loop()
        globals.logger.console(f"Retrieving tracks from playlist {playlist.name}...")
        tracks: Tracks = loop.run_until_complete(
            spotify.net.get_all_tracks(State.get_token(), playlist.id))
        for trackmarker in tracks:
            try:
                globals.logger.console(f'Name: {trackmarker.track_name}')
                globals.logger.console(f'Uri: {trackmarker.track.uri}')
            except AttributeError as err:
                print("")
    
    def on_show_loading_dlg(self, evt: wx.CommandEvent):
        dlg = LoadingDialog(self)
        if dlg.ShowModalWithText("Connecting from the debug menu...") == wx.ID_CANCEL:
            # close running threads here
            pass
        dlg.Destroy()    
    
    def on_about_menu(self, evt: wx.CommandEvent):
        dlg = BubbleDialog(self, -1, "SPBackup", [
            "Spotify Backup", "Coded by Paul Millar", "Beta tested by Conor Moore",
            "version 1.0b", "09-01-2023"
        ], (640, 480))
        dlg.ShowModal()
        dlg.Destroy()

    def on_details(self, event: wx.CommandEvent):
        """Event handler for the Details menu item."""
        asyncio.run(self.app.retrieve_user_info())

    def on_reauth(self, event: wx.CommandEvent):
        """Event handler for the Re-authorize menu item."""
        self.app.reauthenticate()
    
    def toggle_hide_playlists(self, evt: wx.CommandEvent):
        menu: wx.Menu = evt.GetEventObject()
        # make sure the other window isnt split
        if self.hide_tracks_menuitem.IsChecked():
            # uncheck this menuitem and return do nothing
            # this makes sure only one menuitem is checked at a time
            self.hide_playlists_menuitem.Check(False)
            return
        if menu.IsChecked(self.hide_playlists_menuitem.GetId()):
            UI.playlists_spw.Unsplit(UI.playlists_ctrl)
            UI.playlists_ctrl.Disable()
        else:
            UI.playlists_spw.SplitHorizontally(UI.playlists_ctrl, UI.playlistinfo_ctrl)
            UI.playlists_ctrl.Enable()
    
    def toggle_hide_tracks(self, evt: wx.CommandEvent):
        menu: wx.Menu = evt.GetEventObject()
        if self.hide_playlists_menuitem.IsChecked():
            # uncheck this menuitem and return do nothing
            # this makes sure only one menuitem is checked at a time
            self.hide_tracks_menuitem.Check(False)
            return
        if menu.IsChecked(self.hide_tracks_menuitem.GetId()):
            UI.playlists_spw.Unsplit(UI.playlistinfo_ctrl)
        else:
            UI.playlists_spw.SplitHorizontally(UI.playlists_ctrl, UI.playlistinfo_ctrl)



class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        UI.playlists_toolbar = PlaylistsToolBar(self)
        UI.playlists_spw = PlaylistSplitterWindow(self)
        UI.playlistinfo_toolbar = PlaylistInfoToolBar(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(UI.playlists_toolbar, 0, wx.EXPAND, 0)
        vbox.Add(UI.playlists_spw, 1, wx.EXPAND, 0)
        vbox.Add(UI.playlistinfo_toolbar, 0, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(vbox)
