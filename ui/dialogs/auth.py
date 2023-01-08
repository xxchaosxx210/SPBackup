import wx
import ui.style as style

class AuthDialog(wx.Dialog):
    def __init__(self, parent, auth_url):
        super().__init__(parent, title="Authorization Required")

        # Save the auth_url
        self.auth_url = auth_url

        # Set the dialog's background color to the green color used by Spotify
        self.SetBackgroundColour(style.COLOUR_SPOTIFY_BACKGROUND)

        # Create a label
        self.label = wx.StaticText(self, label="Click the Login Button to Authenticate with your Spotify account")

        # Set the label's text color to white
        self.label.SetForegroundColour(style.COLOUR_SPOTIFY_TEXT)

        # Set the label's font to the font used by Spotify
        font = wx.Font(wx.FONTSIZE_MEDIUM, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.label.SetFont(font)

        # Create a button
        self.button = style.create_spotify_button(self, label="Authorize", font_size=16)
        self.button.Bind(wx.EVT_BUTTON, self.on_button)
        # self.button.SetMinSize((200, 50))  # Set the button size

        # Set the button's text color to white
        self.button.SetBackgroundColour(style.COLOUR_SPOTIFY_GREEN)
        self.button.SetForegroundColour(style.COLOUR_SPOTIFY_TEXT)

        # Set the button's font to the font used by Spotify
        self.button.SetFont(font)

        # Create a grid sizer
        sizer = wx.GridSizer(rows=2, cols=1, vgap=0, hgap=0)

        # Add the label and button to the sizer with a span of 2 columns and 2 rows
        sizer.Add(self.label, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(self.button, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        # Set the dialog's sizer
        self.SetSizerAndFit(sizer)

        # Center the dialog on the parent window
        self.CentreOnParent()

        # Remove the close button from the dialog
        self.SetWindowStyle(self.GetWindowStyle() & ~wx.CLOSE_BOX)

    def on_button(self, event):
        # Open the web browser
        wx.LaunchDefaultBrowser(self.auth_url)
        

def demo():
    # Create an application object
    app = wx.App()

    # Create a dialog object
    auth_url = "https://www.spotify.com/authorize"
    dialog = AuthDialog(None, auth_url)

    # Show the dialog
    dialog.ShowModal()

    # Destroy the dialog
    dialog.Destroy()

if __name__ == '__main__':
    demo()
