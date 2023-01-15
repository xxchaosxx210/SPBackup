# URi to be redirected when authorizing using the oauth method
REDIRECT_URI = "http://localhost:3000"

# Playlist permission scopes
PLAYLIST_READ_PRIVATE = "playlist-read-private"
PLAYLIST_MODIFY_PUBLIC = "playlist-modify-public"
PLAYLIST_MODIFY_PRIVATE = "playlist-modify-private"
PLAYLIST_READ_COLLABORATIVE = "playlist-read-collaborative"

# STATUS CODES
STATUS_OK = 200
STATUS_BAD_TOKEN = 401
STATUS_BAD_OAUTH_REQUEST = 403
STATUS_LIMIT_RATE_REACHED = 429

USER_AGENT_HEADER = "SPBackup-App"

# Authenticating Uri
URL_AUTHORIZE = 'https://accounts.spotify.com/authorize'
URL_TOKEN_AUTHENTICATE = "https://accounts.spotify.com/api/token"

# ENDPOINT API URIs
URI_PLAYLISTS = "https://api.spotify.com/v1/me/playlists"
URI_PLAYLIST = lambda playlist_id : f"https://api.spotify.com/v1/playlists/{playlist_id}"
URI_PLAYLIST_TRACKS = lambda playlist_id : f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

URI_USER = "https://api.spotify.com/v1/me"