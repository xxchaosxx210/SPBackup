import requests
import aiohttp
import logging
import spotify.const as const
from spotify.serializers.tracks import Tracks
from spotify.serializers.user import User

logger = logging.getLogger()

import requests

def create_auth_header():
    return {
        'Authorization': f'Basic {const.AUTH_HEADER.decode("utf-8")}'
    }

def create_auth_token_header(token) -> dict:
    return {"Authorization": f"Bearer {token}"}


def authorize(scopes: tuple):
    """authorize(scopes)

    Args:
        scopes (tuple): tuple array of scope strings. Check the const file 

    Returns:
        _type_: returns the response url to follow to authenticate and retrieve the token auth
    """
    # Set up the authorization request
    auth_params = {
        "response_type": "code",
        "redirect_uri": const.REDIRECT_URI,
        "scope": " ".join(scopes),
        "client_id": const.CLIENT_ID,
    }
    response = requests.get(const.URL_AUTHORIZE, params=auth_params)
    response.raise_for_status()
    logger.info(f"Response: {response.__str__()}")
    return response.url

def exchange_code_for_token(code: str) -> str:
    """swap the auth code for a token ID

    Args:
        code (str): auth code, to get this use the RedirectListener, exchange_code_for_token will be called within that thread

    Returns:
        str: returns the access token used to authenticate during API calls
    """
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": const.REDIRECT_URI,
    }
    token_headers = create_auth_header()
    response = requests.post(const.URL_TOKEN_AUTHENTICATE, data=token_data, headers=token_headers)
    logger.info(f"Response: {response.__str__()}")
    response.raise_for_status()
    return response.json()["access_token"]

async def get_playlists(token: str) -> tuple:
  # Set the authorization header with the access token
#   headers = create_auth_token_header(token)
  headers = create_auth_token_header(token)

  # Create an asyncio session to send the request
  async with aiohttp.ClientSession() as session:
    # Send a GET request to the playlist endpoint using the session
    async with session.get(const.URI_PLAYLISTS, headers=headers) as response:
      # If the request was successful, return the list of playlists
      logger.info(f"Response: {response.__str__()}")
      if response.status == 200:
        playlists = await response.json()
        return (
            "ok",
            playlists["items"]
        )
      # If the request was not successful, raise an exception
      return (
        "error",
        response
      )

async def get_user_info(token: str) -> User:
    # Set the authorization header
    headers = create_auth_token_header(token)

    async with aiohttp.ClientSession() as session:
        # Send the GET request
        async with session.get(const.URI_USER, headers=headers) as response:
            # Check the status code
            if response.status != 200:
                return (
                    "error",
                    response
                )

            # Return the user information as a dictionary
            json_response = await response.json()
            return (
                "ok",
                User(**json_response)
            )

def get_playlist(token: str, playlist_id: str) -> dict:
    headers = create_auth_token_header(token)
    # Send the request to the Spotify API
    response = requests.get(const.URI_PLAYLIST(playlist_id), headers=headers)
    logger.info(f"Response: {response.__str__()}")
    # Check the response status code
    response.raise_for_status()
    # Return the playlist data
    return response.json()

def get_playlist_items(token, playlist_id):
  headers = create_auth_token_header(token)

  # Send the request to the API endpoint
  response = requests.get(const.URI_PLAYLIST_TRACKS(playlist_id), headers=headers)
  logger.info(f"Response: {response.__str__()}")
  # Raise an exception if the request fails
  response.raise_for_status()

  # Extract the JSON response
  data = response.json()
  model = TracksModel.from_orm(data)
  return model
