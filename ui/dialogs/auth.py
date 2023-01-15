import wx

class AuthDialog(wx.Dialog):
    def __init__(self, parent, auth_url):
        super().__init__(parent, title="Authorization Required")

        # Save the auth_url
        self.auth_url = auth_url

        # Create a label
        self.label = wx.StaticText(self, 
        label="""Click the Authorize Button to Authenticate with your Spotify account.\n\nNote: You may be required to login in through your Default Web Browser""")

        # Create a button
        self.button = wx.Button(self, label="Authorize")
        self.button.Bind(wx.EVT_BUTTON, self.on_button)

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
