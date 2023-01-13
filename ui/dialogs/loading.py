import wx

class LoadingDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, title="Loading...", style=wx.CAPTION|wx.CLOSE)

        # Create wxGauge
        self.gauge = wx.Gauge(
            self, range=100, size=(250, 25), style=wx.GA_HORIZONTAL)
        self.gauge.SetValue(0)

        # Create a text box
        self.textbox = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)
        # Hide the caret
        self.textbox.SetCaret(wx.Caret(self.textbox, 0, 0))

        # Create cancel button
        self.cancel_button = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        # Create sizers
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add gauge, textbox and cancel button to sizers
        main_sizer.Add(self.gauge, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(self.textbox, 1, wx.EXPAND | wx.ALL, 5)
        h_sizer.Add(self.cancel_button, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h_sizer, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizerAndFit(main_sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetSize((400, 400))
        # Center the dialog on screen
        self.Center()
    
    def OnClose(self, evt: wx.CommandEvent):
        pass
    
    def ShowModalWithText(self, text: str):
        self.reset(0, text)
        return super().ShowModal()
    
    def OnCancel(self, evt: wx.CommandEvent):
        self.EndModal(wx.ID_CANCEL)
    
    def reset(self, range: int, text: str):
        self.gauge.SetRange(range)
        self.update_progress(0, text)

    def update_progress(self, progress: int, text: str):
        self.gauge.SetValue(progress)
        if not text:
            return
        # add text to details
        self.textbox.Freeze()
        self.textbox.AppendText(text)
        last_postion = self.textbox.GetLastPosition()
        self.textbox.ShowPosition(last_postion)
        self.textbox.Thaw()
