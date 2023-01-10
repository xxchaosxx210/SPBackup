import aiohttp
import logging
import asyncio
import spotify.const as const
from spotify.validators.tracks import Tracks
from spotify.validators.user import User
from spotify.validators.playlist_info import PlaylistInfo
from spotify.validators.playlist_info import Tracks
from spotify.validators.playlists import Playlists

from spotify.debug import debug

logger = logging.getLogger()


class SpotifyError(Exception):
    def __init__(self, code: int, text: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_text = text
        self.code = code


def create_auth_header():
    return {"Authorization": f'Basic {const.AUTH_HEADER.decode("utf-8")}'}


def create_auth_token_header(token) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


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
    if response.status == const.STATUS_BAD_TOKEN:
        raise SpotifyError(
            response.status, "Bad or Expired Token. Please Re-Authenticate"
        )
    elif response.status == const.STATUS_BAD_OAUTH_REQUEST:
        raise SpotifyError(
            response.status,
            "Wrong Consumer key, Bad Nonce or expired timestamp. You may need to Logout and Login into your account again",
        )
    elif response.status == const.STATUS_LIMIT_RATE_REACHED:
        raise SpotifyError(response.status, "The App has exceeded its rate")
    else:
        raise SpotifyError(
            response.status,
            f"Unknown status code: {response.status}. Please check Spotify API documentation for the error",
        )


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
            if response.status == const.STATUS_OK:
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
        async with session.post(
            const.URL_TOKEN_AUTHENTICATE, data=token_data, headers=token_headers
        ) as response:
            if response.status == const.STATUS_OK:
                json_response = await response.json()
                return json_response["access_token"]
            raise_spotify_exception(response)


async def get_playlists(
    token: str, url: str = "", offset: int = 0, limit: int = 50
) -> dict:
    headers = create_auth_token_header(token)
    params = {}
    if not url:
        url = const.URI_PLAYLISTS
        params = {"offset": offset, "limit": limit}

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == const.STATUS_OK:
                json_response = await response.json()
                return Playlists(**json_response)
            raise_spotify_exception(response)


async def get_user_info(token: str) -> User:
    # Set the authorization header
    headers = create_auth_token_header(token)

    async with aiohttp.ClientSession() as session:
        # Send the GET request
        async with session.get(const.URI_USER, headers=headers) as response:
            # Check the status code
            if response.status != const.STATUS_OK:
                raise_spotify_exception(response)

            # Return the user information as a dictionary
            json_response = await response.json()
            return User(**json_response)


async def get_playlist(access_token: str, playlist_id: str) -> dict:
    """Retrieve a playlist from the Spotify API

    Args:
        access_token (str): A valid Spotify API access token
        playlist_id (str): The Spotify ID of the playlist

    Returns:
        dict: A dictionary containing the playlist information
    """
    headers = create_auth_token_header(access_token)
    # the fields what we want returned you add more later check the spotify.validators.playlist_info file for the classnames and properties returned
    # dont forget to update that file if you add or remove any more to the fields
    query_params = {
        "fields": "id,name,tracks(items(added_at,track(album,artists,href,uri,name)),next,previous,offset,total)",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            const.URI_PLAYLIST(playlist_id), headers=headers, params=query_params
        ) as response:
            if response.status == const.STATUS_OK:
                json_response = await response.json()
                # sp_debug.save(".get_playlist_output.json", json_response)
                plylist = PlaylistInfo(**json_response)
                return plylist
            raise_spotify_exception(response)


async def get_playlist_tracks(access_token, playlist_id, offset=0, limit=100):
    params = {"offset": offset, "limit": limit}
    headers = create_auth_token_header(access_token)
    async with aiohttp.ClientSession() as session:
        async with session.get(
            const.URI_PLAYLIST_TRACKS(playlist_id), headers, params=params
        ) as response:
            if response.status == const.STATUS_OK:
                data = await response.json()
                return data
            raise_spotify_exception(response)


async def get_tracks_from_url(access_token: str, url: str):
    headers = create_auth_token_header(access_token)
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == const.STATUS_OK:
                tracks = await response.json()
                return Tracks(**tracks)
            raise_spotify_exception(response)
