import wx

class ErrorDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, title: str, message: str):
        super().__init__(parent, title=title)

        # Error icon
        icon = wx.ArtProvider.GetIcon(wx.ART_ERROR, wx.ART_MESSAGE_BOX)
        icon_ctrl = wx.StaticBitmap(self, bitmap=icon)

        # Error message
        message_ctrl = wx.TextCtrl(self, value=message, style=wx.TE_MULTILINE|wx.TE_READONLY)

        # OK button
        close_button = wx.Button(self, id=wx.ID_CLOSE, label="Close")
        self.Bind(wx.EVT_BUTTON, lambda *args: self.Close(), close_button)

        # Add icon and message to main sizer
        main_sizer = wx.GridBagSizer(vgap=5, hgap=5)
        main_sizer.Add(icon_ctrl, pos=(0,0), flag=wx.TOP|wx.LEFT, border=5)
        main_sizer.Add(message_ctrl, pos=(0,1), span=(1,2), flag=wx.EXPAND|wx.ALL, border=5)
        main_sizer.Add(close_button, pos=(1,1), flag=wx.BOTTOM|wx.ALIGN_CENTER, border=5)
        main_sizer.AddGrowableCol(1, 1)
        main_sizer.AddGrowableRow(0, 1)

        self.SetSizerAndFit(main_sizer)
        self.SetSize((500, 300))
        self.CenterOnParent()


def show_dialog(parent: wx.Window, title: str, message: str) -> None:
    dlg = ErrorDialog(parent=parent, title=title, message=message)
    dlg.ShowModal()
    dlg.Destroy()