import threading
import datetime
import os
import queue
import urllib.parse
import http.server
import socketserver
from libs.Actions import Actions
from libs.Helpers import Helpers
log = Helpers.log


class MainThread:
  """
  MainThread runs the main loop that processes commands received from the HTTP server.
  It uses threading events to manage synchronization and stopping.
  """

  @staticmethod
  def run(stop_event: threading.Event, httpd: socketserver.TCPServer, database_file: str):

    while not stop_event.is_set():

      # Getting new command from HTTP server
      try:
        command, parameters, finished_event, success_event = httpd.command_queue.get(timeout=1)
      except queue.Empty:
        continue

      log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
      log(f"Received data on HTTP server:")
      log(f" - Command: {command}")
      log(f" - Parameters: {parameters}")

      try:


        # This command refreshes the database
        #  and eventually updates the composition folder path
        if command == "refresh":
          log("Attempting to refresh database...")
          if "composition_folder" in parameters and parameters["composition_folder"][0]:
            composition_folder = parameters["composition_folder"][0]
            if Actions.refresh_database(composition_folder, database_file):
              success_event.set()
              log("Database refresh command completed.")
            else: 
              log("ERROR: Database refresh command failed.")
          else:
            log("ERROR: Composition folder parameter not provided.")


        # This command creates an info file
        #  for a given ALS file
        elif command == "create_info_file":
          log("Attempting to create info file...")
          if "als_file_path" in parameters and parameters["als_file_path"][0]:
            als_file_path = parameters["als_file_path"][0]
            if Actions.create_info_file(als_file_path):
              success_event.set()
              log("Info file creation command completed.")
            else:
              log("ERROR: Info file creation command failed.")
          else:
            log("ERROR: No ALS file path provided.")


        # This command renames everything of the project
        #  to 'artist - title' format
        elif command == "rename_project":
          log("Attempting to create info file...")
          if ("als_file_path" in parameters and parameters["als_file_path"][0] and
              "artist" in parameters and parameters["artist"][0] and
              "title" in parameters and parameters["title"][0]):
            als_file_path = parameters["als_file_path"][0]
            artist = parameters["artist"][0]
            title = parameters["title"][0]
            if Actions.rename_project(als_file_path, artist, title):
              success_event.set()
              log(f"Project renaming command completed: '{artist} - {title}'.")
            else:
              log("ERROR: Project renaming command failed.")
          else:
            log("ERROR: Missing parameters for project renaming (als_file_path, artist and title required).")


      except Exception as e:
        log(f"ERROR: Main code execution failed: {e}")

      # Signal that the command has been processed
      if finished_event:
        finished_event.set()
      log("Command processing completed.")

    # If out of loop, we are stopping
    httpd.server_close()
    log("Main thread stopping.")


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
    finished_event = threading.Event()
    success_event = threading.Event()

    # Store the command where the worker thread can see it
    self.server.command_queue.put((command, parameters, finished_event, success_event))

    finished = finished_event.wait(15) # Wait up to 15 seconds for the command to be processed
    success = success_event.is_set()

    if finished and success:
      self.send_response(200)
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write(b"OK\n")
    elif finished and not success:
      self.send_response(400)
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write(b"FAILED\n")
    else:
      self.send_response(500)
      self.send_header("Content-Type", "text/plain")
      self.end_headers()
      self.wfile.write(b"REQUEST TIMEOUT\n")
