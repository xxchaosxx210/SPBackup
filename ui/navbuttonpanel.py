import wx
import image_manager


class NavButtonPanel(wx.Panel):

    """should be inherited for the next and previous buttons in our toolbar
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Create the back up and restore buttons
        self.backup_button = wx.BitmapButton(self, wx.ID_ANY, image_manager.load_image("backup.png"))
        self.restore_button = wx.BitmapButton(self, wx.ID_ANY, image_manager.load_image("restore.png"))

        self.backup_button.Bind(wx.EVT_BUTTON, self.on_backup_click)
        self.restore_button.Bind(wx.EVT_BUTTON, self.on_restore_click)

        # Create the prev_button and next_button BitmapButtons
        self.prev_button = wx.BitmapButton(self, wx.ID_ANY, image_manager.load_image("previous.png"))
        self.next_button = wx.BitmapButton(self, wx.ID_ANY, image_manager.load_image("next.png"))

        # Bind the button press event to the corresponding method
        self.prev_button.Bind(wx.EVT_BUTTON, self.on_prev_button)
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next_button)

        # Create a GridSizer with two columns and one row
        sizer = wx.GridSizer(1, 4, 0, 0)

        # Add the backup and restore buttons to the sizer
        sizer.Add(self.backup_button, 0, wx.ALL, 0)
        sizer.Add(self.restore_button, 0, wx.ALL, 0)

        # Add the prev_button and next_button to the sizer
        sizer.Add(self.prev_button, 0, wx.ALL, 0)
        sizer.Add(self.next_button, 0, wx.ALL, 0)

        # Set the sizer of the NavButtonPanel
        self.SetSizer(sizer)

        # Disable the prev_button and next_button
        self.prev_button.Disable()
        self.next_button.Disable()

    def on_prev_button(self, event: wx.CommandEvent):
        # Handle the button press event for the prev_button here
        pass

    def on_next_button(self, event: wx.CommandEvent):
        # Handle the button press event for the next_button here
        pass

    def change_state(self):
        # should be overloaded
        pass

    def on_backup_click(self, evt: wx.CommandEvent):
        pass

    def on_restore_click(self, evt: wx.CommandEvent):
        pass