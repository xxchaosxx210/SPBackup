import wx
import ui.style as style

from spotify.validators.user import User


class UserDialog(wx.Dialog):
    def __init__(self, parent: any, user: User):
        super().__init__(
            parent, title="User Information", style=wx.CAPTION|wx.CLOSE)

        # Center the dialog to the parent
        self.CenterOnParent()
        
        # Set the dialog background color
        self.SetBackgroundColour(style.COLOUR_SPOTIFY_BACKGROUND)

        DISPLAY_FONT_SIZE = wx.FONTSIZE_MEDIUM

        name_label = style.create_spotify_static_text(
            self, label="Name:", font_size=DISPLAY_FONT_SIZE)
        name_value = style.create_spotify_static_text(
            self, label=user.display_name, font_size=DISPLAY_FONT_SIZE)

        # Create the followers text
        followers_label = style.create_spotify_static_text(
            self, label=f"Followers:", font_size=DISPLAY_FONT_SIZE)
        folowers_value = style.create_spotify_static_text(
            self, label=str(user.followers.total), font_size=DISPLAY_FONT_SIZE)

        # Create the close button
        close_button = style.create_spotify_button(
            parent=self, id=wx.ID_CLOSE, label="Close")

        # Bind the close button click event
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        # remove the ability to close the button from the dialog window
        self.Bind(wx.EVT_CLOSE, lambda *args: args)


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

        # Set the dialog size
        self.SetSize((300, 300))

    def on_close(self, event):
        # Close the dialog
        self.EndModal(wx.ID_CLOSE)
        

def create_dialog(parent: any, userinfo: User):
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