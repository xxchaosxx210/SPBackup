import requests
import spotify.const as const
from spotify.serializers.tracks import Model as TracksModel

import requests

def create_auth_header():
    return {
        'Authorization': f'Basic {const.AUTH_HEADER.decode("utf-8")}'
    }

def authorize():
    # Set up the authorization request
    auth_params = {
        "response_type": "code",
        "redirect_uri": const.REDIRECT_URI,
        "scope": " ".join(const.PLAYLIST_SCOPES),
        "client_id": const.CLIENT_ID,
    }
    response = requests.get(
        const.AUTH_URL, 
        params=auth_params)
    response.raise_for_status()
    return response.url

def exchange_code_for_token(code: str) -> str:
    """swap the auth code for a token ID

    Args:
        code (str): auth code, to get this use the RedirectListener, exchange_code_for_token will be called within that thread

    Returns:
        str: _description_
    """
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": const.REDIRECT_URI,
    }
    token_headers = create_auth_header()
    response = requests.post(const.TOKEN_BASED_AUTH, data=token_data, headers=token_headers)
    response.raise_for_status()
    return response.json()["access_token"]

def get_playlists(token: str) -> list:
    response = requests.get('https://api.spotify.com/v1/me/playlists', headers={
        'Authorization': f'Bearer {token}'
    })
    response.raise_for_status()
    return response.json()["items"]

def get_playlist(token: str, playlist_id: str) -> dict:
    # Set the authorization header
    auth_header = f"Bearer {token}"
    headers = {
        "Authorization": auth_header
    }
    # Send the request to the Spotify API
    response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)
    # Check the response status code
    response.raise_for_status()
    # Return the playlist data
    return response.json()

def get_playlist_items(access_token, playlist_id):
  # Set the API endpoint
  api_endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

  # Set the headers
  headers = {
    "Authorization": f"Bearer {access_token}"
  }

  # Send the request to the API endpoint
  response = requests.get(api_endpoint, headers=headers)

  # Raise an exception if the request fails
  response.raise_for_status()

  # Extract the JSON response

  data = response.json()

  model = TracksModel.from_orm(data)
  return model
