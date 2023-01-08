import wx
import ui.style as style


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
        self.SetBackgroundColour(style.COLOUR_SPOTIFY_BACKGROUND)

        DISPLAY_FONT_SIZE = wx.FONTSIZE_MEDIUM

        name_label = style.create_spotify_static_text(self, label="Name:", font_size=DISPLAY_FONT_SIZE)
        name_value = style.create_spotify_static_text(self, user.display_name, font_size=DISPLAY_FONT_SIZE)

        # Create the followers text
        followers_label = style.create_spotify_static_text(self, label=f"Followers:", font_size=DISPLAY_FONT_SIZE)
        folowers_value = style.create_spotify_static_text(self, label=str(user.followers.total), font_size=DISPLAY_FONT_SIZE)

        # Create the close button
        close_button = style.create_spotify_button(parent=self, label="Close")

        # Bind the close button click event
        close_button.Bind(wx.EVT_BUTTON, self.on_close)


        gs = wx.GridSizer(2, 2, 0, 0)
        gs.Add(name_label, 0, wx.ALL, 0)
        gs.Add(name_value, 0, wx.ALL, 0)
        gs.Add(followers_label, 0, wx.ALL, 0)
        gs.Add(folowers_value, 0, wx.ALL, 0)

        # Create the sizer
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gs, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 10)
        sizer.AddStretchSpacer(1)
        sizer.Add(close_button, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
        self.SetSizerAndFit(sizer)

        # Remove the close button at the top right corner
        self.SetWindowStyle(self.GetWindowStyle() & ~wx.CLOSE_BOX)

    def on_close(self, event):
        # Close the dialog
        self.Close()
        

def show_user_info_dialog(parent, userinfo):
    dlg = UserDialog(parent, userinfo)
    dlg.ShowModal()
    dlg.Destroy()

def demo():
    # Create an application object
    app = wx.App()
    
    dialog = UserDialog(None, "Conor Moore")

    # Show the dialog
    dialog.ShowModal()

    # Destroy the dialog
    dialog.Destroy()

if __name__ == '__main__':
    demo()