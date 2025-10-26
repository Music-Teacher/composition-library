import threading
import urllib.parse
import http.server

from libs.Helpers import Helpers

log = Helpers.log

class HTTPHandler(http.server.BaseHTTPRequestHandler):
  """
  HTTPHandler handles a simple GET request.
  It reads the command from the URL path and parameters from the query string.
  It places the command and parameters into a queue for processing by the main thread.
  It uses threading events to signal completion and success back to the HTTP thread.
  """

  def do_GET(self):
    # Strip leading '/' and keep the raw command string
    urlparsed = urllib.parse.urlparse(self.path)
    command = urlparsed.path.lstrip('/')
    parameters = urllib.parse.parse_qs(urlparsed.query)
    log(f"Received HTTP GET command: '{command}' with parameters: {parameters}")

    # Create event to sync between backend and HTTP thread
    no_timeout_event = threading.Event()
    success_event = threading.Event()

    # Store the command where the worker thread can see it
    self.server.command_queue.put((command, parameters, no_timeout_event, success_event))

    no_timeout = no_timeout_event.wait(15) # Wait up to 15 seconds for the command to be processed
    success = success_event.is_set()

    if no_timeout and success:
      self.send_response(200)
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write(b"OK\n")
    elif no_timeout and not success:
      self.send_response(400)
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write(b"FAILED\n")
    else:
      self.send_response(500)
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write(b"REQUEST TIMEOUT\n")
