import wx
from wx.lib.buttons import GenButton

# color codes for the Spotify color scheme
COLOUR_SPOTIFY_BACKGROUND = "#191414"
COLOUR_SPOTIFY_TEXT = "#FFFFFF"
COLOUR_SPOTIFY_GREEN = "#1DB954"

# font used by Spotify
# FONT_SPOTIFY = wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)

def create_spotify_button(parent, label="", font_size=12):
    # Create a button
    button: GenButton = GenButton(parent, label=label)

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

def create_spotify_static_text(parent, label, font_size: 12):
    label: wx.StaticText = wx.StaticText(parent, -1, label=label)
    label.SetForegroundColour(COLOUR_SPOTIFY_TEXT)
    font: wx.Font = label.GetFont()
    font.SetPointSize(font_size)
    label.SetFont(font)
    return label