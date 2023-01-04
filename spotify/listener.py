import threading
import socket
from urllib.parse import parse_qs
from spotify.net import exchange_code_for_token
import time

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
                    # Parse the query string of the received data
                    query_string = parse_qs(data)
                    # Extract the code from the query string
                    string = query_string["GET /?code"][0]
                    first_space = string.index(" ")
                    code = string[:first_space]
                    # Seems to be an issue with responding soon after. Set delay to get auth token
                    time.sleep(2)
                    token = exchange_code_for_token(code)
                    self.callback("token", token)
                    # Set the stop event
                    self.stop_event.set()

    def stop(self):
        """Stop the listener"""
        self.stop_event.set()

# # Create an instance of the class
# listener = RedirectListener(3000, "your-client-id", "your-client-secret")

# # Start the listener
# list
