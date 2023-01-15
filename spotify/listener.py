import threading
import socket
import urllib.parse
from typing import Callable

import spotify.net
from spotify import debugging

PORT = 3000
HOST = "localhost"

HTML = """
<html>
  <head>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
      html {
        font-family: 'Roboto', sans-serif;
      }

      body {
        background-color: #282828;
        color: #ffffff;
      }

      .container {
        background-color: #121212;
        border: 2px solid #1db954;
        border-radius: 5px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 1rem;
      }

      h2 {
        text-align: center;
        color: #1db954;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <h2>You are now authorized. You can now close this page and use the SPBackup app</h2>
    </div>
  </body>
</html>


"""


class RedirectListener(threading.Thread):

    EVENT_SOCKET_ERROR = 0
    EVENT_TOKEN_RECIEVED = 1
    EVENT_REQUESTING_AUTHORIZATION = 2
    EVENT_SPOTIFY_ERROR = 3
    EVENT_AUTHORIZATION_ERROR = 4

    def __init__(self, 
                app_name: str,
                client_id: str,
                client_secret: str,
                mainthread_callback: Callable[[int], any]):
        """constructor

        Args:
            app_name (str): the app name to be added to the User-Agent header
            mainthread_callback (function): the function callback the caller should take
            parameters of state: str and value: any doesnt require a return value
        """
        super().__init__()
        self.stop_event = threading.Event()
        self.callback = mainthread_callback
        self.app_name = app_name
        self.client_id = client_id
        self.client_secret = client_secret

    def run(self):
        """listen on a localhost waits for a redirect link and sends a token to callback if successful
        change the HOST and PORT constants in the spotify.const module to change the host and port address
        Note: That this is for testing only!!!
        """
        self.callback(RedirectListener.EVENT_REQUESTING_AUTHORIZATION, None)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while not self.stop_event.is_set():
                try:
                    conn, addr = s.accept()
                    with conn:
                        # send the HTML response to the user that they are authenticated
                        self.send_response(conn, HTML)
                        # recieve the code (Hopefully)
                        http_response = conn.recv(1024).decode()
                        # defragment the headers
                        parsed_data = urllib.parse.urlparse(http_response)
                        # Parse the query string of the received data into a dict 'code=our_code'
                        query: dict = urllib.parse.parse_qs(parsed_data.query)

                        # force an error
                        # query = {"give-me-an-error": None}
                        # check for code key in query dict
                        if not query.get("code", None) or len(query["code"]) < 1:
                            # there is an issue could not find code as first element
                            _error_message = f"Error: could not find Authorize Code in HTTP response... {http_response}"
                            debugging.file_log(_error_message, "error")
                            self.callback(
                                RedirectListener.EVENT_AUTHORIZATION_ERROR,
                                _error_message,
                            )
                            self.stop_event.set()
                            break
                        # another step required as the http contents are still in the query.
                        # we will need to split the code from the rest of the http header.
                        # good thing is the code is seperated by a space. so slice from the first space
                        # in the string back to the first character. That should be our code
                        string = query["code"][0]
                        first_space = string.index(" ")
                        code = string[:first_space]
                        try:
                            # send an async request to obtain the token
                            token = spotify.net.await_on_sync_call(
                                spotify.net.exchange_code_for_token, 
                                client_id=self.client_id,
                                client_secret=self.client_secret,
                                code=code)
                            # all went well we should now have an auth token
                            self.callback(RedirectListener.EVENT_TOKEN_RECIEVED, token)
                        except spotify.net.SpotifyError as err:
                            self.callback(RedirectListener.EVENT_SPOTIFY_ERROR, err)
                        finally:
                            self.stop_event.set()
                except socket.error as err:
                    # Should be a network issue
                    debugging.file_log(
                        f"Error in RedirectListener reading from socket. {err.__str__()}",
                        "error",
                    )
                    self.callback(RedirectListener.EVENT_SOCKET_ERROR, err)

    def send_response(self, conn: socket.socket, html: str):
        # Set the response to an HTML page that says "Thank you"
        response = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\nUser-Agent: {self.app_name}\r\n\r\n"
        response += html
        conn.sendall(response.encode())

    def stop(self):
        """Stop the listener"""
        self.stop_event.set()
