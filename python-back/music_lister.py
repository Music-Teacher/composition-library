import os
import sys
import datetime
import time
import threading
import socketserver
import queue
import platform

from libs.HTTPHandler import HTTPHandler
from libs.Composition import Composition
from libs.MusicLister import MusicLister
from libs.Helpers import Helpers

log = Helpers.log

# DEFAULT GLOBAL PARAMETERS
# Database export file
DATABASE_FILE = None
# Folder to search into for compositions
COMPOSITIONS_FOLDER = None
#####

# Current script path
CURRENT_SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
DESIGN_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "design.css")
JS_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "sortfilter.js")

# TCP server parameters
SOCKET_HOST = "localhost"
SOCKET_PORT = 5555

# Refresh database
def refresh_database(composition_folder, database_file):
  if composition_folder:
    ml = MusicLister(composition_folder, database_file)
    ml.export_json()
  else:
    log("ERROR: No composition folder set yet.")

# Create info file
def create_info_file(als_file_path):
  info_file_path = Helpers.get_info_file_related_to_als(als_file_path)
  if not info_file_path:
    info_file_path = Helpers.get_info_file_name_from_als(als_file_path)
    with open(info_file_path, 'w') as info_file:
      for field in Composition.get_info_file_fields():
        info_file.write(f"{field}: \n")
    log(f"Info file created: {info_file_path}")
  else:
    log(f"Info file already exists: {info_file_path}")

def main_thread(stop_event: threading.Event, httpd: socketserver.TCPServer):

  global COMPOSITIONS_FOLDER
  global DATABASE_FILE

  while not stop_event.is_set():
    try:
      command, parameters, no_timeout_event, success_event = httpd.command_queue.get(timeout=1)
    except queue.Empty:
      command, parameters, no_timeout_event, success_event = None, None, None, None

    if not command:
      continue

    log(f"Received data on HTTP server: '{command}' '{parameters}'")

    try:
      command_valid = command in ["refresh", "create_info_file"]
      if command_valid:
        log(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if command == "refresh":
          log("Scanning for compositions...")
          if "composition_folder" in parameters and parameters["composition_folder"][0]:
            new_potential_composition_folder = parameters["composition_folder"][0]
            if os.path.isdir(new_potential_composition_folder):
              log(f"New compositions folder: {new_potential_composition_folder}")
              COMPOSITIONS_FOLDER = new_potential_composition_folder
              if success_event:
                success_event.set()
            else:
              log(f"Error: Path is invalid {new_potential_composition_folder}")
          else:
            if success_event:
              success_event.set()

          log(f"Will use: {COMPOSITIONS_FOLDER}")

          refresh_database(COMPOSITIONS_FOLDER, DATABASE_FILE)

        elif command == "create_info_file":
          if "als_file_path" in parameters and parameters["als_file_path"][0]:
            als_file_path = parameters["als_file_path"][0]
            create_info_file(als_file_path)
            if success_event:
              success_event.set()
          else:
            log("Error: No ALS file path provided.")

    except Exception as e:
      log(f"Error during main code execution: {e}")
    finally:
      if no_timeout_event:
        no_timeout_event.set()

  httpd.server_close()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    log("Usage: python music_lister.py <database_file_path>")
    sys.exit(1)

  DATABASE_FILE = sys.argv[1]
  if not os.path.isdir(os.path.dirname(DATABASE_FILE)):
    log(f"Error: The directory for the database file does not exist: {os.path.dirname(DATABASE_FILE)}")
    sys.exit(1)

  log(f"OS: {platform.system()}")
  log(f"Using database file: {DATABASE_FILE}")

  log("Starting music_lister...")
  # Create the HTTP server (no threading – we’ll drive it manually)
  httpd = socketserver.TCPServer((SOCKET_HOST, SOCKET_PORT), HTTPHandler, bind_and_activate=False)
  httpd.allow_reuse_address = True
  httpd.server_bind()
  httpd.server_activate()
  httpd.last_command = None
  httpd.command_queue = queue.Queue()

  stop_flag = threading.Event()    
  main_thread = threading.Thread(target=main_thread, args=(stop_flag, httpd), daemon=True)
  log(f"Program running on HTTP server ({SOCKET_HOST}:{SOCKET_PORT})")
  main_thread.start()
  
  server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
  server_thread.start()

  try:
    # Main thread can stay idle or do other work.
    while True:
      time.sleep(5)
      if not main_thread.is_alive():
        log("Main thread has stopped unexpectedly. Stopping program.")
        break
  except KeyboardInterrupt:
    log(f"\nStopping program… Please wait for completion (can take a few seconds)…")
    stop_flag.set()
    main_thread.join()
    httpd.server_close()
    httpd.shutdown()
    server_thread.join
  log("Program music_lister stopped.")
