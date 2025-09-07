import os
import re
import sys
import threading
import datetime
import time
import json
import socketserver
import http.server
import queue

# USER PARAMETERS
# Set the folder to search
COMPOSITIONS_FOLDER="/mnt/c/Users/obrun/Music/Compositions"
#####

# Current script path
CURRENT_SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
DESIGN_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "design.css")
JS_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "sortfilter.js")

# Timeout and update frequency
UPDATE_FREQUENCY = 30
SOCKET_HOST = "localhost"
SOCKET_PORT = 5555

class Composition:
  """This class will hold the composition information.
  It will look for an info file on disk, based on the ALS file path given."""

  name = None
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
  audio_file = None
  last_activity = None

  def __init__(self, als_file_path, root_folder=None):
    self.als_file_path = als_file_path
    self.root_folder = root_folder
    self.project_dir = os.path.dirname(als_file_path)
    self.als_file_name = os.path.basename(als_file_path)
    modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(als_file_path))
    self.last_activity = modification_time.strftime("%Y-%m-%d %H:%M")
    self.audio_file = Helpers.get_audio_file_related_to_als(self.als_file_path)
    self.gather_composition_information()

  def gather_composition_information(self):
    info_file_path = Helpers.get_info_file_related_to_als(self.als_file_path)
    if info_file_path:
      info = Helpers.get_fields_from_file(info_file_path)
      self.name = info.get("name", self.als_file_name) or self.als_file_name
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

  def __str__(self):
    return_string = f"# {self.artist+" - " if self.artist else ""}{self.name}\n"
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
    audio_generated = "exported" if self.audio_file else "not exported"
    return_string += f" -> Audio file {audio_generated}"
    return return_string

  def __json__(self, python=True):
    j = dict()
    
    j["name"] = self.name
    j["artist"] = self.artist
    j["album"] = self.album
    j["ep"] = self.ep
    j["lyrics"] = self.lyrics
    j["chords"] = self.chords
    j["extra_info"] = self.extra_info
    j["status"] = self.status
    j["rework"] = self.rework

    j["als_file_path"] = self.als_file_path
    j["project_dir"] = self.project_dir
    j["root_folder"] = self.root_folder
    j["als_file_name"] = self.als_file_name
    j["audio_file"] = self.audio_file
    j["last_activity"] = self.last_activity

    if python:
      return j
    else:
      return json.dumps(j, indent=2)


class MusicLister:
  """This class will look for Ableton Live Sets.
  It will find them in the root_folder path."""

  root_folder = None
  compositions = dict()

  def __init__(self, root_folder):
    assert os.path.isdir(root_folder)
    self.root_folder = root_folder
    self.output_json_file = os.path.abspath(os.path.join("..", "database", "database.json"))
    self.look_for_als(root_folder)
  
  def look_for_als(self, path):
    if Helpers.is_als(path):
      self.compositions[path] = Composition(path, self.root_folder)
    
    if os.path.isfile(path):
      return

    als_present = Helpers.is_als_present_in_path(path)

    for element in os.listdir(path):
      next_path = os.path.join(path, element)
      if als_present and os.path.isdir(next_path):
        continue
      self.look_for_als(next_path)

  def export_json(self):
    print(f"Exporting JSON library to: {self.output_json_file}")
    file = open(self.output_json_file, 'w')
    file.write(self.__json__(python=False))
    file.close()
  
  def __str__(self):
    return_string = f"\n###################\nRoot folder: {self.root_folder}\n"
    return_string += f"Number of compositions: {len(self.compositions)}\n"
    return_string += "\n"
    for name in self.compositions:
      return_string += f"{self.compositions[name]}"
    return_string += f"###################"
    return return_string
  
  def __json__(self, python=True):
    j = dict()
    j["root_folder"] = self.root_folder
    j["output_json_file"] = self.output_json_file
    j["number_of_compositions"] = len(self.compositions)
    j["compositions"] = dict()
    id = 0
    for name in self.compositions:
      j["compositions"][id] = self.compositions[name].__json__()
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
  def get_audio_file_related_to_als(path):
    file_path = path.replace(".als", ".wav")
    if os.path.isfile(file_path):
      return file_path
    return None

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
  def replace_wsl_disk_with_windows(path):
    return re.sub(r'/mnt/([a-z]{1})', r'\1:', path)


class SimpleHTTPHandler(http.server.BaseHTTPRequestHandler):
  """Handles a single GET request."""

  def do_GET(self):
    # Strip leading '/' and keep the raw command string
    command = self.path.lstrip('/')

    # Create event to sync between backend and HTTP thread
    no_timeout_event = threading.Event()
    success_event = threading.Event()

    # Store the command where the worker thread can see it
    self.server.command_queue.put((command, no_timeout_event, success_event))

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
def main_code():
  ml = MusicLister(COMPOSITIONS_FOLDER)
  ml.export_json()

def main_thread(stop_event: threading.Event, httpd: socketserver.TCPServer):

  next_refresh_time = time.time() # To start, right now

  while not stop_event.is_set():
    try:
      command, no_timeout_event, success_event = httpd.command_queue.get(timeout=1)
    except queue.Empty:
      command, no_timeout_event, success_event = None, None, None

    if command:
      print(f"Received data on HTTP server: '{command}'")

    try:
      command_valid = command in ["refresh"]
      auto_refresh = command is None and time.time() >= next_refresh_time

      if command_valid or auto_refresh:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        data = "SUCCESS"
        if command == "refresh" or auto_refresh:
          print("Scanning for compositions...")
          main_code()
          next_refresh_time = time.time() + UPDATE_FREQUENCY

        if success_event:
          success_event.set()

    except Exception as e:
      print(f"Error during main code execution: {e}")
    finally:
      if no_timeout_event:
        no_timeout_event.set()

  httpd.server_close()

if __name__ == "__main__":
  print("Starting music_lister...")
  # Create the HTTP server (no threading – we’ll drive it manually)
  httpd = socketserver.TCPServer((SOCKET_HOST, SOCKET_PORT), SimpleHTTPHandler, bind_and_activate=False)
  httpd.allow_reuse_address = True
  httpd.server_bind()
  httpd.server_activate()
  httpd.last_command = None
  httpd.command_queue = queue.Queue()

  stop_flag = threading.Event()    
  main_thread = threading.Thread(target=main_thread, args=(stop_flag, httpd), daemon=True)
  print(f"Program running on HTTP server ({SOCKET_HOST}:{SOCKET_PORT}) and max update time every {UPDATE_FREQUENCY}s.")
  main_thread.start()
  
  server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
  server_thread.start()

  try:
    # Main thread can stay idle or do other work.
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    print(f"\nStopping program… Please wait for completion (can take up to {UPDATE_FREQUENCY}s)…")
    stop_flag.set()
    main_thread.join()
    httpd.server_close()
    httpd.shutdown()
    server_thread.join()
  print("Program music_lister stopped.")
