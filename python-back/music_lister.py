import os
import re
import sys
import glob
import threading
import datetime
import time
import json
import socketserver
import http.server
import queue
import urllib.parse
import platform

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

class Composition:
  """This class will hold the composition information.
  It will look for an info file on disk, based on the ALS file path given."""

  title = None
  artist = None
  album = None
  ep = None
  lyrics = None
  chords = None
  extra_info = None
  status = None
  rework = None

  als_file_path = None
  project_dir = None
  root_folder = None
  als_file_name = None
  audio_files = None
  last_activity = None

  def __init__(self, als_file_path, root_folder=None):
    self.als_file_path = als_file_path
    self.root_folder = root_folder
    self.project_dir = os.path.dirname(als_file_path)
    self.als_file_name = os.path.basename(als_file_path)
    modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(als_file_path))
    self.last_activity = modification_time.strftime("%Y-%m-%d %H:%M")
    self.audio_files = Helpers.get_audio_files_related_to_als(self.als_file_path)
    self.title = None
    self.artist = None
    self.album = None
    self.ep = None
    self.lyrics = None
    self.chords = None
    self.extra_info = None
    self.status = None
    self.rework = None
    self.gather_composition_information()

  def gather_composition_information(self):
    info_file_path = Helpers.get_info_file_related_to_als(self.als_file_path)
    if info_file_path:
      info = Helpers.get_fields_from_file(info_file_path)
      self.title = info.get("title", self.als_file_name) or self.als_file_name
      self.artist = info.get("artist", None) or None
      self.album = info.get("album", None) or None
      self.ep = info.get("ep", None) or None
      self.lyrics = info.get("lyrics", None) or None
      self.extra_info = info.get("extra_info", None) or None
      self.chords = info.get("chords", None) or None
      self.status = info.get("status", None) or None
    self.make_proper_info()
  
  def make_proper_info(self):
    if self.status and Helpers.is_status_complete(self.status):
      self.status = "Finished"
      self.rework = None
    else:
      self.rework = self.status
      self.status = "In Progress"
  
  def is_finished(self):
    return self.status == "Finished"

  def getShortenedFilePath(self):
    if self.root_folder:
      return os.path.relpath(self.als_file_path, self.root_folder)
    return self.als_file_path

  def __str__(self):
    local_artist = f"{self.artist} - " if self.artist else ""
    return_string = f"# {local_artist}{self.title}\n"
    return_string += f"Last activity: {self.last_activity}"
    if self.album:
      return_string += f"-- Album: {self.album}"
    return_string += f" + Status: {self.status}\n"
    if self.rework:
      return_string += f" + Rework: {self.rework}\n"
    if self.chords:
      return_string += f" - Chords:\n"
      return_string += f"{self.chords}\n"
    if self.lyrics:
      return_string += f" - Lyrics:\n"
      return_string += f"{self.lyrics}\n"
    if self.extra_info:
      return_string += f" - Extra Info:\n"
      return_string += f"{self.extra_info}\n"
    return_string += f"{self.als_file_path}\n\n"
    audio_generated = "exported" if self.audio_files else "not exported"
    return_string += f" -> Audio file {audio_generated}"
    return return_string

  def __json__(self, python=True):
    j = dict()
    
    j["title"] = self.title
    j["artist"] = self.artist
    j["album"] = self.album
    j["ep"] = self.ep
    j["lyrics"] = self.lyrics
    j["chords"] = self.chords
    j["extra_info"] = self.extra_info
    j["status"] = self.status
    j["rework"] = self.rework

    j["als_file_path"] = self.getShortenedFilePath()
    j["project_dir"] = self.project_dir
    j["root_folder"] = self.root_folder
    j["als_file_name"] = self.als_file_name
    j["audio_files"] = self.audio_files
    j["audio"] = (self.audio_files != None and len(self.audio_files) > 0)
    j["last_activity"] = self.last_activity

    if python:
      return j
    else:
      return json.dumps(j, indent=2)


class MusicLister:
  """This class will look for Ableton Live Sets.
  It will find them in the root_folder path."""

  root_folder = None

  def __init__(self, root_folder, output_json_file):
    assert os.path.isdir(root_folder)
    self.compositions = dict()
    self.root_folder = root_folder
    self.output_json_file = os.path.abspath(output_json_file)
    self.look_for_als(root_folder)
  
  def look_for_als(self, path):
    """"Recursively look for Ableton Live Sets in the given path."""

    # If ALS file, add it to the list
    if Helpers.is_als(path):
      self.compositions[path] = Composition(path, self.root_folder)

    # If file but not ALS, ignore
    if os.path.isfile(path):
      return

    # Check if ALS present in this folder
    als_present = Helpers.is_als_present_in_path(path)

    # Browse all elements (files and dirs) in this folder
    for element in os.listdir(path):
      next_path = os.path.join(path, element)
      # If ALS present in this folder, don't look at dirs below
      if als_present and os.path.isdir(next_path):
        continue
      self.look_for_als(next_path)

  def export_json(self):
    log(f"Exporting JSON library to: {self.output_json_file}")
    file = open(self.output_json_file, 'w')
    file.write(self.__json__(python=False))
    file.close()
  
  def __str__(self):
    return_string = f"\n###################\nRoot folder: {self.root_folder}\n"
    return_string += f"Number of compositions: {len(self.compositions)}\n"
    return_string += "\n"
    for title in self.compositions:
      return_string += f"{self.compositions[title]}"
    return_string += f"###################"
    return return_string
  
  def __json__(self, python=True):
    j = dict()
    j["root_folder"] = self.root_folder
    j["output_json_file"] = self.output_json_file
    j["number_of_compositions"] = len(self.compositions)
    j["compositions"] = []
    id = 0
    for title in self.compositions:
      dict_id = f"{id}-{abs(hash(self.compositions[title].als_file_path))}"
      composition_dict = self.compositions[title].__json__()
      composition_dict["id"] = dict_id
      j["compositions"].append(composition_dict)
      id = id + 1
    
    if python:
      return j
    else:
      return json.dumps(j, indent=2)


class Helpers:
  """This helper class contains all basic functions as static."""

  @staticmethod
  def is_als(path):
    return os.path.isfile(path) and ".als" in path

  @staticmethod
  def is_infofile(path):
    return os.path.isfile(path) and ".info" in path

  @staticmethod
  def is_als_present_in_path(path):
    if os.path.isfile(path):
      return False
    for element in os.listdir(path):
      als_potential_path = os.path.join(path, element)
      if Helpers.is_als(als_potential_path):
        return True
    return False

  @staticmethod
  def get_info_file_related_to_als(path):
    file_path = path.replace(".als", ".txt")
    if os.path.isfile(file_path):
      return file_path
    return None
  
  @staticmethod
  def is_audio_file(file_path):
    if not os.path.isfile(file_path):
      return False
    list_of_extensions = ["mp3", "wav", "ogg"]
    file_name = os.path.basename(file_path)
    if '.' in file_name and file_name.split('.')[-1] in list_of_extensions:
      return True
    return False

  @staticmethod
  def get_audio_files_related_to_als(als_file_path):
    audio_files = []
    als_dir = os.path.dirname(als_file_path)
    files = list(filter(os.path.isfile, glob.glob(als_dir + "/*")))
    files.sort(key=lambda x: os.path.getmtime(x))
    files.reverse()
    for file in files:
      if Helpers.is_audio_file(file):
        audio_files.append(os.path.join(als_dir, file))
    return audio_files

  @staticmethod
  def get_fields_from_file(path):
    fields = dict()

    # Function to save field
    def save_field(filed_name, field_value):
      if field_name and field_value:
        fields[field_name.strip()] = field_value.strip()

    with open(path) as file:
      field_name = None
      field_value = None
      for line in file:
        line = line.strip()
        try:
          key, value = line.split(':', 1)
          save_field(field_name, field_value)
          field_name = key
          field_value = value
        except:
          if field_name:
            field_value += f"\n{line}"
          pass
      save_field(field_name, field_value)
    return fields

  @staticmethod
  def is_status_complete(status):
    pattern = r'(?i)^(?:finished|complete|completed)$'
    match = re.findall(pattern, status.strip())
    if match:
      return True
    return False
  
  @staticmethod
  def get_fields_from_param(param):
    if param and '=' in param:
      try:
        key, value = param.split('=', 1)
        return (key, value)
      except:
        pass
    return (None, None)

  @staticmethod
  def log(message):
    print(f"[{datetime.datetime.now()}] {message}", flush=True)

log = Helpers.log

class SimpleHTTPHandler(http.server.BaseHTTPRequestHandler):
  """Handles a single GET request."""

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


# Main code
def main_code(composition_folder, database_file):
  if composition_folder:
    ml = MusicLister(composition_folder, database_file)
    ml.export_json()
  else:
    log("ERROR: No composition folder set yet.")

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
      command_valid = command in ["refresh"]
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

          main_code(COMPOSITIONS_FOLDER, DATABASE_FILE)

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
  httpd = socketserver.TCPServer((SOCKET_HOST, SOCKET_PORT), SimpleHTTPHandler, bind_and_activate=False)
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
