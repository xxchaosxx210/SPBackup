import wx
import os

ICON_PATH = os.path.join("images", "SPBackup_icon.ico")

def load_image(filename):
    """Load an image file and return a wx.Image object.

    Parameters:
    filename (str): The name of the image file to load.

    Returns:
    wx.Image: The image object.
    """
    # Use the os.path.join function to build the filepath based on the operating system
    filepath = os.path.join("images", filename)

    # Load the image using the wx.Image class
    image = wx.Image(filepath, wx.BITMAP_TYPE_ANY)

    return image
