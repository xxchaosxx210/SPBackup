import wx

class AuthDialog(wx.Dialog):
    def __init__(self, parent, auth_url):
        super().__init__(parent, title="Authorization Required")

        # Save the auth_url
        self.auth_url = auth_url

        # Create a label
        self.label = wx.StaticText(self, label="Click the Login Button to Authenticate with your Spotify account")

        # Create a button
        self.button = wx.Button(self, label="Authorize")
        self.button.Bind(wx.EVT_BUTTON, self.on_button)
        self.button.SetMinSize((200, 50))  # Set the button size

        # Create a sizer and add the label and button to it
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.label, 0, wx.ALL, 10)
        sizer.Add(self.button, 0, wx.ALIGN_CENTER | wx.ALL, 10)  # Center the button

        # Set the dialog's sizer
        self.SetSizer(sizer)

        self.SetWindowStyle(self.GetWindowStyle() & ~wx.CLOSE_BOX)

    def on_button(self, event):
        # Open the web browser
        wx.LaunchDefaultBrowser(self.auth_url)