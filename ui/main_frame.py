import wx
import asyncio
from ui.playlist_splitterwindow import PlaylistSplitterWindow
from ui.playlist_ctrl import PlaylistInfoToolBar
from ui.playlists_ctrl import PlaylistsToolBar
from globals.state import UI
import image_manager
from ui.dialogs.bubbledialog import BubbleDialog

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
        menu_bar = wx.MenuBar()

        # Create a User menu
        user_menu = wx.Menu()

        # Create a Details menu item
        details_item = wx.MenuItem(user_menu, wx.ID_ANY, "Details")
        user_menu.Append(details_item)
        self.Bind(wx.EVT_MENU, self.on_details, details_item)

        # Create a Re-authorize menu item
        reauth_item = wx.MenuItem(user_menu, wx.ID_ANY, "Re-authorize")
        user_menu.Append(reauth_item)
        self.Bind(wx.EVT_MENU, self.on_reauth, reauth_item)

        # Add the User menu to the menu bar
        menu_bar.Append(user_menu, "User")

        # View Menu creation
        view_menu = wx.Menu()

        # Create a Hide Playlists MenuItem
        self.hide_playlists_menuitem = wx.MenuItem(view_menu, wx.ID_ANY, "Hide Playlists", kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggle_hide_playlists, self.hide_playlists_menuitem)
        view_menu.Append(self.hide_playlists_menuitem)
        # Create a Hide Tracks MenuItem
        self.hide_tracks_menuitem = wx.MenuItem(view_menu, wx.ID_ANY, "Hide Tracks", kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_MENU, self.toggle_hide_tracks, self.hide_tracks_menuitem)
        view_menu.Append(self.hide_tracks_menuitem)

        menu_bar.Append(view_menu, "View")

        help_menu = wx.Menu()
        about_menuitem = wx.MenuItem(help_menu, wx.ID_ANY, "About")
        self.Bind(wx.EVT_MENU, self.on_about_menu, about_menuitem)
        help_menu.Append(about_menuitem)

        menu_bar.Append(help_menu, "Help")

        # Set the frame's menu bar
        self.SetMenuBar(menu_bar)
    
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
