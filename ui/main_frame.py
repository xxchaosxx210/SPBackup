import wx
import asyncio

from ui.playlist_splitterwindow import PlaylistSplitterWindow
from ui.playlist_ctrl import PlaylistInfoToolBar
from ui.playlists_ctrl import PlaylistsToolBar
from ui.dialogs.bubbledialog import BubbleDialog
from ui.dialogs.loading import LoadingDialog

from globals.state import UI
from globals.state import State
import globals.logger

from spotify.validators.playlist import Playlist
import spotify.net

import image_manager


class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetIcon(wx.Icon(image_manager.ICON_PATH))
        self.main_panel = MainPanel(self)

        # store the global statusbar
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
        self.details_item = wx.MenuItem(self.user_menu, wx.ID_ANY, "Details")
        self.reauth_item = wx.MenuItem(self.user_menu, wx.ID_ANY, "Re-authorize")
        self.Bind(wx.EVT_MENU, self.on_user_details, self.details_item)
        self.Bind(wx.EVT_MENU, self.on_reauthenticate, self.reauth_item)
        self.user_menu.Append(self.details_item)
        self.user_menu.Append(self.reauth_item)


        # View Menu creation
        self.view_menu = wx.Menu()
        self.hide_playlists_menuitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, "Hide Playlists", kind=wx.ITEM_CHECK)
        self.hide_tracks_menuitem = wx.MenuItem(
            self.view_menu, wx.ID_ANY, "Hide Tracks", kind=wx.ITEM_CHECK)
        self.Bind(
            wx.EVT_MENU, self.toggle_hide_playlists, self.hide_playlists_menuitem)
        self.Bind(
            wx.EVT_MENU, self.toggle_hide_tracks, self.hide_tracks_menuitem)
        self.view_menu.Append(self.hide_playlists_menuitem)
        self.view_menu.Append(self.hide_tracks_menuitem)

        # Debug menu creation
        self.debug_menu = wx.Menu()
        self.all_tracks = wx.MenuItem(self.debug_menu, wx.ID_ANY, "Get All Tracks")
        show_loading_dlg = wx.MenuItem(self.debug_menu, wx.ID_ANY, "Show Loading Dialog")
        self.Bind(wx.EVT_MENU, self.on_show_loading_dlg, show_loading_dlg)
        self.Bind(wx.EVT_MENU, 
            lambda evt : asyncio.create_task(self.on_get_all_tracks()), 
            self.all_tracks)
        self.debug_menu.Append(self.all_tracks)
        self.debug_menu.Append(show_loading_dlg)

        # Help menu
        self.help_menu = wx.Menu()
        self.about_menuitem = wx.MenuItem(self.help_menu, wx.ID_ANY, "About")
        self.Bind(wx.EVT_MENU, self.on_about_menu, self.about_menuitem)
        self.help_menu.Append(self.about_menuitem)

        # Append the menus to the menubar
        self.menu_bar.Append(self.user_menu, "User")
        self.menu_bar.Append(self.view_menu, "View")
        self.menu_bar.Append(self.debug_menu, "Debug")
        self.menu_bar.Append(self.help_menu, "Help")

        # Set the frame's menu bar
        self.SetMenuBar(self.menu_bar)

    async def on_get_all_tracks(self, *args):
        """debug menu - get all the tracks belonging to the selected playlist
        """
        # get the first selected item from the listctrl
        index = UI.playlists_ctrl.GetFirstSelected()
        if index == -1:
            return
        # get the playlist information to display to the console
        playlist: Playlist = State.get_playlists().items[index]
        globals.logger.console(f"Retrieving tracks from playlist {playlist.name}...")
        # get the generator and iterate through
        dlg = LoadingDialog(self, playlist.tracks.total, "Loading all tracks...")
        dlg.Show(True)
        # import threading
        # threading.Thread(target=dlg.Show).start()
        async for item in spotify.net.get_all_track_items(
            State.get_token(), playlist.id):
            try:
                dlg.update_progress()
                dlg.append_text(text=f"Loaded {item.track.name}.")
            except (AttributeError, TypeError) as err:
                globals.logger.console(
                    f"Error updating the progress of all tracks. {err.__str__()}", "error")
        dlg.complete()
    
    def on_show_loading_dlg(self, evt: wx.CommandEvent):
        """debug menu - show a loading dialog for testing purposes

        Args:
            evt (wx.CommandEvent): never used
        """
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

    def on_user_details(self, event: wx.CommandEvent):
        """Event handler for the Details menu item."""
        asyncio.get_event_loop().create_task(wx.GetApp().retrieve_user_info())

    def on_reauthenticate(self, event: wx.CommandEvent):
        """Event handler for the Re-authorize menu item."""
        wx.GetApp().reauthenticate()
    
    def toggle_hide_playlists(self, evt: wx.CommandEvent):
        """toggles the hide and show functions in the splitterwindow

        Args:
            evt (wx.CommandEvent): _description_
        """
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
        """toggles the hide and show functions in the splitterwindow

        Args:
            evt (wx.CommandEvent): _description_
        """
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
