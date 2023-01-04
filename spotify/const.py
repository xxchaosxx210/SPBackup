import base64

CLIENT_ID = "615b6e76033644d5b4cb68b7e11cbeb4"
CLIENT_SECRET = "88130c005e2041e98f1529e5f7aaf6e3"

REDIRECT_URI = "http://localhost:3000"

PLAYLIST_SCOPES = (
    "playlist-read-private",
    "playlist-modify-public",
    "playlist-modify-private",
    "playlist-read-collaborative"
)

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_BASED_AUTH = "https://accounts.spotify.com/api/token"

AUTH_HEADER = base64.b64encode(
    f'{CLIENT_ID}:{CLIENT_SECRET}'.encode('utf-8'))

ACCESS_TOKEN = None