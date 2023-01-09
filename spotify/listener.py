import threading
import socket
from urllib.parse import (
  urlparse,
  parse_qs
)
from spotify.net import exchange_code_for_token
from spotify.net import SpotifyError
from spotify.net import await_on_sync_call
from spotify.debug import debug

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

    def __init__(self, port, client_id, client_secret, app_name, mainthread_callback):
        super().__init__()
        self.port = port
        self.stop_event = threading.Event()
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback = mainthread_callback
        self.app_name = app_name

    def run(self):
        """Listen for a redirect on the specified port"""
        self.callback(RedirectListener.EVENT_REQUESTING_AUTHORIZATION, None)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, self.port))
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
                        parsed_data = urlparse(http_response)
                        # Parse the query string of the received data into a dict 'code=our_code'
                        query: dict = parse_qs(parsed_data.query)
                        string = query["code"][0]
                        # check for code key in query dict
                        if not query.get("code", None) or len(query["code"]) < 1:
                          # there is an issue
                          self.callback(RedirectListener.EVENT_CODE_ERROR, f"Error: could not find Auth Code in HTTP response... {http_response}")
                          self.stop_event.set()
                          return
                        string = query["code"][0]
                        first_space = string.index(" ")
                        code = string[:first_space]
                        try:
                            # send an async request to obtain the token
                            token = await_on_sync_call(exchange_code_for_token, code=code)
                            # all went well we should now have an auth token
                            self.callback(RedirectListener.EVENT_TOKEN_RECIEVED, token)
                        except SpotifyError as err:
                            self.callback(RedirectListener.EVENT_SPOTIFY_ERROR, err)
                        finally:
                          self.stop_event.set()
                except socket.error as err:
                  # Should be a network issue
                    debug.file_log(f"Error in RedirectListener reading from socket. {err.__str__()}", "error")
                    self.callback(RedirectListener.EVENT_SOCKET_ERROR, err)
    
    def send_response(self, conn, html):
        # Set the response to an HTML page that says "Thank you"
        response = f"HTTP/1.1 200 OK\nContent-Type: text/html\n\nUser-Agent: {self.app_name}\r\n\r\n"
        response += html
        conn.sendall(response.encode())


    def stop(self):
        """Stop the listener"""
        self.stop_event.set()
