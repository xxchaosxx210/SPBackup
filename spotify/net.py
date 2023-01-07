import aiohttp
import logging
import asyncio
import spotify.const as const
from spotify.serializers.tracks import Tracks
from spotify.serializers.user import User
from spotify.serializers.playlist_info import Playlist as PlaylistInfo

logger = logging.getLogger()


class SpotifyError(Exception):

    def __init__(self, code: int, text: str):
        self.response_text = text
        self.code = code


def create_auth_header():
    return {
        'Authorization': f'Basic {const.AUTH_HEADER.decode("utf-8")}'
    }

def create_auth_token_header(token) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def await_on_sync_call(func_to_wait_on, **kwargs) -> any:
    """for synchronous calls to the spotify api

    Args:
        func_to_wait_on (_type_): Python function
        **kwargs: keyword arguments to be passed into the func_to_wait_on

    Returns:
        any: whatever return object is returned form the func_to_wait_on function
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    value = loop.run_until_complete(func_to_wait_on(**kwargs))
    return value

def raise_spotify_exception(response: aiohttp.ClientResponse):
    """checks the response.status and raises a SpotifyError

    Args:
        response (aiohttp.ClientResponse): the server response from the Spotify API

    Raises:
        SpotifyError: _description_
        SpotifyError: _description_
        SpotifyError: _description_
        SpotifyError: _description_
    """
    if response.status == 401:
        raise SpotifyError(response.status, "Bad or Expired Token. Please Re-Authenticate")
    elif response.status == 403:
        raise SpotifyError(response.status, "Wrong Consumer key, Bad Nonce or expired timestamp. You may need to Logout and Login into your account again")
    elif response.status == 429:
        raise SpotifyError(response.status, "The App has exceeded its rate")
    else:
        raise SpotifyError(response.status, f'Unknown status code: {response.status}. Please check Spotify API documentation for the error')

async def authorize(scopes: tuple):
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
    async with aiohttp.ClientSession() as session:
        async with session.get(const.URL_AUTHORIZE, params=auth_params) as response:
            if response.status == 200:
                url = response.url.human_repr()
                return url
            raise_spotify_exception(response)

async def exchange_code_for_token(code: str) -> str:
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
    async with aiohttp.ClientSession() as session:
        async with session.post(const.URL_TOKEN_AUTHENTICATE, data=token_data, headers=token_headers) as response:
            if response.status == 200:
                json_response = await response.json()
                return json_response["access_token"]
            raise_spotify_exception(response)
    # response = requests.post(const.URL_TOKEN_AUTHENTICATE, data=token_data, headers=token_headers)
    # if response.status == 200:
    #     return response.json()["access_token"]
    # raise_spotify_exception(response)

async def get_playlists(token: str) -> tuple:
  # Set the authorization header with the access token
#   headers = create_auth_token_header(token)
  headers = create_auth_token_header(token)

  # Create an asyncio session to send the request
  async with aiohttp.ClientSession() as session:
    # Send a GET request to the playlist endpoint using the session
    async with session.get(const.URI_PLAYLISTS, headers=headers) as response:
      # If the request was successful, return the list of playlists
      if response.status == 200:
        json_response = await response.json()
        return json_response["items"]
      # If the request was not successful, raise an exception
      raise_spotify_exception(response)

async def get_user_info(token: str) -> User:
    # Set the authorization header
    headers = create_auth_token_header(token)

    async with aiohttp.ClientSession() as session:
        # Send the GET request
        async with session.get(const.URI_USER, headers=headers) as response:
            # Check the status code
            if response.status != 200:
                raise_spotify_exception(response)

            # Return the user information as a dictionary
            json_response = await response.json()
            return User(**json_response)

# async def get_playlist(token: str, playlist_id: str) -> dict:
#     headers = create_auth_token_header(token)

#     async with aiohttp.ClientSession() as session:
#         async with session.get(const.URI_PLAYLIST(playlist_id), headers=headers) as response:
#             if response.status == 200:
#                 return await response.json()
#             raise_spotify_exception(response)
    # Send the request to the Spotify API
    # response = requests.get(const.URI_PLAYLIST(playlist_id), headers=headers)
    # logger.info(f"Response: {response.__str__()}")
    # # Check the response status code
    # response.raise_for_status()
    # # Return the playlist data
    # return response.json()

async def get_playlist(access_token: str, playlist_id: str) -> dict:
    """Retrieve a playlist from the Spotify API

    Args:
        access_token (str): A valid Spotify API access token
        playlist_id (str): The Spotify ID of the playlist

    Returns:
        dict: A dictionary containing the playlist information
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    query_params = {
        "fields": "name,tracks(items(added_at,track(album,artists,href,uri,name)))",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            const.URI_PLAYLIST(playlist_id),
            headers=headers,
            params=query_params
        ) as response:
            if response.status == 200:
                json_response = await response.json()
                plylist = PlaylistInfo(**json_response)
                return plylist
            raise_spotify_exception(response)

async def get_playlist_items(access_token: str, playlist_id: str, limit: int = 20, offset: int = 0) -> dict:
    """Retrieve the items in a playlist from the Spotify API

    Args:
        access_token (str): A valid Spotify API access token
        playlist_id (str): The Spotify ID of the playlist
        limit (int, optional): The maximum number of items to retrieve. Defaults to 20.
        offset (int, optional): The index of the first item to retrieve. Defaults to 0.

    Returns:
        dict: A dictionary containing the playlist items
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    headers = create_auth_token_header(access_token)
    
    params = {
        "limit": limit,
        "offset": offset,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks",
            headers=headers,
            params=params,
        ) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 403:
                raise SpotifyError(code=response.status, response_text="Rejected. Please logout and login to your account again from Spotify")
            else:
                raise SpotifyError(code=response.status, response_text="An error occurred while retrieving the playlist items")

async def get_playlist_items(token, playlist_id):
  headers = create_auth_token_header(token)

  # Send the request to the API endpoint
#   response = requests.get(const.URI_PLAYLIST_TRACKS(playlist_id), headers=headers)
#   logger.info(f"Response: {response.__str__()}")
#   # Raise an exception if the request fails
#   response.raise_for_status()

#   # Extract the JSON response
#   data = response.json()
#   model = Tracks.from_orm(data)
#   return model
