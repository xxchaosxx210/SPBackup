import wx
import asyncio
from ui.playlist_splitterwindow import PlaylistSplitterWindow
from ui.playlist_ctrl import PlaylistInfoToolBar
from ui.playlists_ctrl import PlaylistsToolBar

class MainFrame(wx.Frame):

    def __init__(self, app=None, *args, **kw):
        super().__init__(*args, **kw)

        self.app = app

        self.main_panel = MainPanel(self)

        self.sbar = self.CreateStatusBar()

        self.create_menubar()

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, 0)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, 1, wx.ALL|wx.EXPAND, 0)

        self.SetSizerAndFit(vbox)
        self.SetSize((800, 800))


    def create_menubar(self):
        """Creates the menu bar."""
        # Create a menu bar
        menu_bar = wx.MenuBar()

        # Create a User menu
        user_menu = wx.Menu()

        # Create a Details menu item
        details_item = wx.MenuItem(user_menu, wx.ID_ANY, "Details")
        user_menu.Append(details_item)

        # Bind an event handler to the menu item
        self.Bind(wx.EVT_MENU, self.on_details, details_item)

        # Create a Re-authorize menu item
        reauth_item = wx.MenuItem(user_menu, wx.ID_ANY, "Re-authorize")
        user_menu.Append(reauth_item)

        # Bind an event handler to the menu item
        self.Bind(wx.EVT_MENU, self.on_reauth, reauth_item)

        # Add the User menu to the menu bar
        menu_bar.Append(user_menu, "User")

        # Set the frame's menu bar
        self.SetMenuBar(menu_bar)

    def on_details(self, event):
        """Event handler for the Details menu item."""
        asyncio.run(self.app.retrieve_user_info())

    def on_reauth(self, event):
        """Event handler for the Re-authorize menu item."""
        self.app.reauthenticate()

class MainPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.playlists_toolbar = PlaylistsToolBar(self)
        self.playlists_spw = PlaylistSplitterWindow(self)
        self.playlistinfo_toolbar = PlaylistInfoToolBar(self)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.playlists_toolbar, 0, wx.EXPAND, 0)
        vbox.Add(self.playlists_spw, 1, wx.EXPAND, 0)
        vbox.Add(self.playlistinfo_toolbar, 0, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(vbox)
