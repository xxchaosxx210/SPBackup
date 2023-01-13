import wx
from wx.lib.buttons import GenButton

# color codes for the Spotify color scheme
COLOUR_SPOTIFY_BACKGROUND = "#191414"
COLOUR_SPOTIFY_TEXT = "#FFFFFF"
COLOUR_SPOTIFY_GREEN = "#1DB954"

# font used by Spotify
# FONT_SPOTIFY = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

def create_spotify_button(
    parent: wx.Panel, id: int = -1, label: str = "", font_size: int = 12) -> wx.Button:
    # Create a button
    button: GenButton = GenButton(parent, id=id, label=label)

    # Set the button's background color to the green color used by Spotify
    button.SetBackgroundColour(COLOUR_SPOTIFY_GREEN)

    # Set the button's text color to white
    button.SetForegroundColour(COLOUR_SPOTIFY_TEXT)

    # Set the button's font to the font used by Spotify
    font: wx.Font = button.GetFont()
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    font.SetPointSize(font_size)
    button.SetFont(font)

    button.SetBezelWidth(0)

    # Return the button
    return button

def create_spotify_static_text(
    parent: wx.Panel, id: int = -1, label: str = "", font_size: int = 12) -> wx.StaticText:
    """creates a spotify styled statictext

    Args:
        parent (wx.Panel): _description_
        label (str, optional): _description_. Defaults to "".
        font_size (int, optional): _description_. Defaults to 12.

    Returns:
        wx.StaticText: _description_
    """
    static_text: wx.StaticText = wx.StaticText(parent, id=id, label=label)
    static_text.SetForegroundColour(COLOUR_SPOTIFY_TEXT)
    font: wx.Font = static_text.GetFont()
    font.SetPointSize(font_size)
    static_text.SetFont(font)
    return static_text