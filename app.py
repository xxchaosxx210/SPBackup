import wx
from main_frame import MainFrame

class SPBackupApp(wx.App):

    def __init__(self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)


def run_app():
    spbackup_app = SPBackupApp()
    frame = MainFrame(None, title="Spotify Backup - coded by Paul Millar")
    frame.Show()
    spbackup_app.MainLoop()

if __name__ == '__main__':
    run_app()