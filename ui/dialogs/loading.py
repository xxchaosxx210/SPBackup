import wx
from datetime import datetime


class LoadingDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, max_range: int, first_message: str):
        wx.Dialog.__init__(
            self, parent, title="Loading...", style=wx.CAPTION|wx.CLOSE)

        self.textbox = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        # Create wxGauge
        self.gauge = wx.Gauge(
            self, range=100, size=(250, 25), style=wx.GA_HORIZONTAL)
        self.reset(max_range, first_message)

        self.cancel_button = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")
        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        main_sizer.Add(self.gauge, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(self.textbox, 1, wx.EXPAND | wx.ALL, 5)
        h_sizer.Add(self.cancel_button, 0, wx.ALL | wx.CENTER, 5)
        main_sizer.Add(h_sizer, 0, wx.ALL | wx.CENTER, 5)

        self.SetSizerAndFit(main_sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetSize((400, 400))
        self.Center()
    
    def OnClose(self, evt: wx.CommandEvent):
        pass
    
    def ShowModalWithText(self, text: str):
        self.reset(0, text)
        return super().ShowModal()
    
    def OnCancel(self, evt: wx.CommandEvent):
        wx.CallAfter(self.EndModal(wx.ID_CANCEL))
    
    def reset(self, range: int, text: str):
        self.gauge.SetRange(range)
        self.gauge.SetValue(0)
        self.textbox.Clear()
        self.append_text(text)

    def update_progress(self):
        """update the gauge by 1
        """
        value: int = self.gauge.GetValue()
        self.gauge.SetValue(value + 1)
    
    def append_text(self, text: str):
        """appends text to new line and scrolls window down if bottom of textctrl

        Args:
            text (str): _description_
        """
        self.textbox.Freeze()
        self.textbox.AppendText(f"{text}\n")
        last_postion = self.textbox.GetLastPosition()
        self.textbox.ShowPosition(last_postion)
        self.textbox.Thaw()

    def complete(self):
        now = datetime.now()
        time_str = now.strftime("%d-%m-%y %H:%M:%S")
        self.append_text(f"Task completed on: {time_str}")