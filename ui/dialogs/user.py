import wx

from spotify.validators.user import User


class UserDialog(wx.Dialog):
    def __init__(self, parent: any, user: User):
        super().__init__(
            parent, title="User Information", style=wx.CAPTION|wx.CLOSE)

        name_label = wx.StaticText(self, label="Name:")
        name_value = wx.StaticText(self, label=user.display_name)

        # Create the followers text
        followers_label = wx.StaticText(self, label="Followers:")
        folowers_value = wx.StaticText(
            self, label=str(user.followers.total))

        # Create the close button
        close_button = wx.Button(parent=self, id=wx.ID_CLOSE, label="Close")

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
        # Center the dialog to the parent
        self.CenterOnParent()

    def on_close(self, event):
        # Close the dialog
        self.EndModal(wx.ID_CLOSE)
        

def create_dialog(parent: any, userinfo: User):
    dlg = UserDialog(parent, userinfo)
    dlg.ShowModal()
    dlg.Destroy()