import wx

class UserDialog(wx.Dialog):
    def __init__(self, parent, user):
        super().__init__(parent, title="User Information")

        # Get the parent size
        parent_width, parent_height = parent.GetSize()

        # Set the dialog size
        self.SetSize((parent_width // 2, parent_height // 2))

        # Center the dialog to the parent
        self.CenterOnParent()

        # Set the dialog background color
        self.SetBackgroundColour("#191414")

        # Create the display_name text
        display_name_text = wx.StaticText(self, label=f"Display Name: {user.display_name}")
        display_name_text.SetForegroundColour("#FFFFFF")

        # Create the followers text
        followers_text = wx.StaticText(self, label=f"Followers: {user.followers.total}")
        followers_text.SetForegroundColour("#FFFFFF")

        # Create the close button
        close_button = wx.Button(self, label="Close")
        close_button.SetBackgroundColour("#1DB954")
        close_button.SetForegroundColour("#FFFFFF")

        # Bind the close button click event
        close_button.Bind(wx.EVT_BUTTON, self.on_close)

        # Create the sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(display_name_text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        sizer.Add(followers_text, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 10)
        sizer.Add(close_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.SetSizer(sizer)

        # Remove the close button at the top right corner
        self.SetWindowStyle(self.GetWindowStyle() & ~wx.CLOSE_BOX)

    def on_close(self, event):
        # Close the dialog
        self.Close()
        

def show_user_info_dialog(parent, userinfo):
    dlg = UserDialog(parent, userinfo)
    dlg.ShowModal()
    dlg.Destroy()