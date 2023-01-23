import wx


class CreateBackupDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title='Create Backup')

        # Create Backup Name StaticBox
        backup_name_staticbox = wx.StaticBox(self, label='Backup Name')
        backup_name_sizer = wx.StaticBoxSizer(backup_name_staticbox, wx.VERTICAL)
        self.backup_name_textctrl = wx.TextCtrl(self)
        backup_name_sizer.Add(self.backup_name_textctrl, flag=wx.EXPAND | wx.ALL)

        # Create Backup Description StaticBox
        backup_description_staticbox = wx.StaticBox(
            self, label='Backup Description')
        backup_description_sizer = wx.StaticBoxSizer(backup_description_staticbox, wx.VERTICAL)
        self.backup_description_textctrl = wx.TextCtrl(self)
        backup_description_sizer.Add(
            self.backup_description_textctrl, flag=wx.EXPAND | wx.ALL)

        # Create buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ok_button = wx.Button(self, wx.ID_OK, label='OK')
        self.cancel_button = wx.Button(self, wx.ID_CANCEL, label='Cancel')
        button_sizer.Add(self.ok_button, flag=wx.ALL, border=5)
        button_sizer.Add(self.cancel_button, flag=wx.ALL, border=5)

        # Create main sizer and add all elements
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(backup_name_sizer, flag=wx.EXPAND | wx.ALL, border=5)
        main_sizer.Add(backup_description_sizer,
                       flag=wx.EXPAND | wx.ALL, border=5)
        main_sizer.Add(button_sizer, flag=wx.ALIGN_CENTER)
            # Set sizer and center the dialog
        self.SetSizerAndFit(main_sizer)
        self.CenterOnParent()

    def get_name_and_description(self) -> tuple:
        return (
            self.backup_name_textctrl.GetValue(),
            self.backup_description_textctrl.GetValue()
        )