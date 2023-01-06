import threading
import socket
from urllib.parse import parse_qs
from spotify.net import exchange_code_for_token
from spotify.net import SpotifyError
import asyncio

PORT = 3000

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
    def __init__(self, port, client_id, client_secret, mainthread_callback):
        super().__init__()
        self.port = port
        self.stop_event = threading.Event()
        self.client_id = client_id
        self.client_secret = client_secret
        self.callback = mainthread_callback

    def run(self):
        """Listen for a redirect on the specified port"""
        self.callback("authorize", None)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("localhost", self.port))
            s.listen()
            while not self.stop_event.is_set():
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024).decode()
                    self.send_response(conn, HTML)
                    # Parse the query string of the received data
                    query_string = parse_qs(data)
                    # Extract the code from the query string
                    string = query_string["GET /?code"][0]
                    first_space = string.index(" ")
                    code = string[:first_space]
                    try:
                        # token = exchange_code_for_token(code)
                        loop = asyncio.new_event_loop()
                        token = loop.run_until_complete(exchange_code_for_token(code))
                        self.callback("token", token)
                    except SpotifyError as err:
                        self.callback("spotify-error", err)
                    # Set the stop event
                    self.stop_event.set()
    
    def send_response(self, conn, html):
        # Set the response to an HTML page that says "Thank you"
        response = "HTTP/1.1 200 OK\nContent-Type: text/html\n\n"
        response += html #"<html><body>Thank you</body></html>"
        conn.sendall(response.encode())


    def stop(self):
        """Stop the listener"""
        self.stop_event.set()
