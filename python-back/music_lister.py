import os
import sys
import datetime
import time
import multiprocessing
import threading
import socketserver
import queue
import platform

from libs.ConnectionHandler import HTTPHandler, MainThread
from libs.Composition import Composition
from libs.MusicLister import MusicLister
from libs.Helpers import Helpers

log = Helpers.log

DATABASE_FILE = None
SOCKET_HOST = "localhost"
SOCKET_PORT = 5555

if __name__ == "__main__":
  if len(sys.argv) != 2:
    log("Usage: python music_lister.py <database_file_path>")
    sys.exit(1)

  DATABASE_FILE = sys.argv[1]
  if not os.path.isdir(os.path.dirname(DATABASE_FILE)):
    log(f"ERROR: The directory for the database file does not exist: {os.path.dirname(DATABASE_FILE)}")
    sys.exit(1)

  log(f"OS: {platform.system()}")
  log(f"Using database file: {DATABASE_FILE}")
  log(f"Using socket: {SOCKET_HOST}:{SOCKET_PORT}")

  log("Creating the HTTP server (no threading – we’ll drive it manually)...")
  httpd = socketserver.TCPServer((SOCKET_HOST, SOCKET_PORT), HTTPHandler, bind_and_activate=False)
  httpd.allow_reuse_address = True
  httpd.server_bind()
  httpd.server_activate()
  httpd.last_command = None
  httpd.block_on_close = False
  httpd.command_queue = queue.Queue()
  log(f"Server created on {SOCKET_HOST}:{SOCKET_PORT}.")

  log("Launching main program thread...")
  stop_flag = threading.Event()    
  main_thread = threading.Thread(target=MainThread.run, args=(stop_flag, httpd, DATABASE_FILE), daemon=True)
  main_thread.start()
  log(f"Main thread running.")

  log("Launching HTTP server thread...")
  server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
  server_thread.start()
  log("HTTP server running.")

  try:
    # Main thread can stay idle or do other work.
    while True:
      time.sleep(5)
      if not main_thread.is_alive():
        log("Main thread has stopped unexpectedly. Stopping program.")
        break
  except KeyboardInterrupt:
    log("Keyboard interrupt received.")

  log(f"Stopping program… Please wait for completion (can take a few seconds)…")

  log("Waiting for main thread to stop...")
  stop_flag.set()
  main_thread.join(timeout=2)

  log("Shutdown HTTP...")
  httpShutdown = threading.Thread(target=httpd.shutdown, daemon=True)
  httpShutdown.start()

  log("Waiting for shutdown to finish...")
  httpShutdown.join(timeout=2)

  log("Waiting for server thread to stop...")
  server_thread.join(timeout=2)

  log("Program stopped.")
