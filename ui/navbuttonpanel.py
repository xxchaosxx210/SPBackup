import wx
import image_manager

import wx
import image_manager

class NavButtonPanel(wx.Panel):

    """should be inherited for the next and previous buttons in our toolbar
    """

    def __init__(self, parent):
        super().__init__(parent)

        # Create the prev_button and next_button BitmapButtons
        self.prev_button = wx.BitmapButton(self, wx.ID_ANY, image_manager.load_image("previous.png"))
        self.next_button = wx.BitmapButton(self, wx.ID_ANY, image_manager.load_image("next.png"))

        # Bind the button press event to the corresponding method
        self.prev_button.Bind(wx.EVT_BUTTON, self.on_prev_button)
        self.next_button.Bind(wx.EVT_BUTTON, self.on_next_button)

        # Create a GridSizer with two columns and one row
        sizer = wx.GridSizer(1, 2, 0, 0)

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