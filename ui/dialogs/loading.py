import wx
import asyncio
from datetime import datetime
from typing import List, Callable


class LoadingDialog(wx.Dialog):
    def __init__(self,
                 parent: wx.Window,
                 max_range: int,
                 title: str,
                 tasks: List[asyncio.Task]):
        """loads an async loading progress dialog with text output

        Args:
            parent (wx.Window): the parent window
            max_range (int): max limit to load to
            title (str): The first message to display
            tasks (List[asyncio.Task]): list of Tasks to cancel if user pressed the cancel button
        """
        wx.Dialog.__init__(
            self, parent, title="Loading...", style=wx.CAPTION | wx.CLOSE)

        self.tasks = tasks

        self.textbox = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)

        # Create wxGauge
        self.gauge = wx.Gauge(
            self, range=100, size=(250, 25), style=wx.GA_HORIZONTAL)
        self.reset(max_range, title)

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

    def cancel_tasks(self):
        for task in self.tasks:
            task.cancel()

    def OnCancel(self, evt: wx.CommandEvent):
        if self.cancel_button.GetValue() == "Cancel":
            self.cancel_tasks()
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
        # change the label to Close as that indicates to not cancel any running tasks
        self.cancel_button.SetLabel("Close")


# for global dialog instance
def show_loading_dialog(
        parent: wx.Window,
        dialog: LoadingDialog,
        callback: Callable[[LoadingDialog], None],
        range: int,
        title: str,
        tasks: List[asyncio.Task]):
    """these are long winded function parameters. so the callback is for
    assigning the global instance of the LoadingDialog. The problem passing
    the global instance as a reference if the instance is equal to None
    obviously doesnt have an address yet so to counter act this I added a callback
    which takes in callback(LoadingDialog) to allow to keep a reference of the global
    LoadingDialog...

    Args:
        parent (wx.Window): the parent window to which this dialog belongs
        dialog (LoadingDialog): global instance if not is None
        callback (Callable[[LoadingDialog], None]): the callback to notify the new instance of the loading dialog
        range (int): maximum range of the progress
        title (str): the first line in the console
        tasks (List[asyncio.Task]): the tasks to cancel if the cancel button is pressed

    Raises:
        RuntimeError: will be raised if trying to create a new dialog while the exsiting one is still showing
    """
    if dialog is not None and dialog.IsShown():
        raise RuntimeError(
            "Loading Dialog instance already exists. Please close the other Dialog first")
    dialog = LoadingDialog(parent=parent, max_range=range,
                           title=title, tasks=tasks)
    dialog.Show(show=True)
    callback(dialog)
    # call dialog.complete() to destroy the dialog


def update_loading_dialog(dialog: LoadingDialog, line: str):
    if dialog is None or not dialog.IsShown():
        raise RuntimeError(
            "Cannot update Progress as Dialog has not been created or is not Showing")
    dialog.update_progress()
    dialog.append_text(text=line)
