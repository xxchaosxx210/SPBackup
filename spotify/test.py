import base64
import requests
import const

# Create a base64 encoded string of your client ID and client secret separated by a colon
auth_header = base64.b64encode(f'{const.CLIENT_ID}:{const.CLIENT_SECRET}'.encode('utf-8'))

# Set the authorization header
headers = {
    'Authorization': f'Basic {auth_header.decode("utf-8")}'
}

# Request the playlist-read-private, playlist-modify-private, and playlist-modify-public scopes
response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data={
    'grant_type': 'client_credentials',
    'scope': 'playlist-read-private playlist-modify-private playlist-modify-public'
})

# If the request was successful, the response will contain an access token that you can use to authenticate your requests to the Spotify API
if response.status_code == 200:
    access_token = response.json()['access_token']
    print(f'Successfully authenticated with access token: {access_token}')
else:
    print(f'Failed to authenticate with status code {response.status_code}')
