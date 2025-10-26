import os
import datetime
import json
from libs.Helpers import Helpers
log = Helpers.log


class Composition:
  """
  Composition represents a musical composition.
  It extracts and holds metadata from the ALS file and its related info file.
  It can provide a string representation and a JSON representation of itself.
  """

  # Data from the info file
  title = None
  artist = None
  album = None
  ep = None
  lyrics = None
  chords = None
  extra_info = None
  status = None

  # Data derived from status
  rework = None

  # Data from the ALS file path
  als_file_path = None
  root_folder = None
  project_dir = None
  als_file_name = None
  info_file_path = None
  last_activity = None
  audio_files = None
  coverart = None

  @staticmethod
  def get_info_file_fields():
    return [
      "title",
      "artist",
      "album",
      "ep",
      "lyrics",
      "chords",
      "extra_info",
      "status"
    ]

  def __init__(self, als_file_path, root_folder=None):
    self.als_file_path = als_file_path
    self.root_folder = root_folder
    self.project_dir = os.path.dirname(als_file_path)
    self.als_file_name = os.path.basename(als_file_path)
    self.info_file_path = Helpers.get_info_file_related_to_als(self.als_file_path)
    modification_time = datetime.datetime.fromtimestamp(os.path.getmtime(als_file_path))
    self.last_activity = modification_time.strftime("%Y-%m-%d %H:%M")
    self.audio_files = Helpers.get_audio_files_related_to_als(self.als_file_path)
    self.coverart = Helpers.get_coverart(self.als_file_path)

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
    info = Helpers.get_fields_from_file(self.info_file_path, Composition.get_info_file_fields()) if self.info_file_path else dict()

    self.title = info.get("title", None)
    self.artist = info.get("artist", None)
    self.album = info.get("album", None)
    self.ep = info.get("ep", None)
    self.lyrics = info.get("lyrics", None)
    self.extra_info = info.get("extra_info", None)
    self.chords = info.get("chords", None)
    self.status = info.get("status", None)

    if self.status and Helpers.is_status_complete(self.status):
      self.rework = None
      self.status = "Finished"
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
    j["full_als_file_path"] = self.als_file_path
    j["info_file"] = True if self.info_file_path else False
    j["project_dir"] = self.project_dir
    j["root_folder"] = self.root_folder
    j["als_file_name"] = self.als_file_name
    j["audio_files"] = self.audio_files
    j["audio"] = (self.audio_files != None and len(self.audio_files) > 0)
    j["coverart"] = self.coverart
    j["last_activity"] = self.last_activity

    if python:
      return j
    else:
      return json.dumps(j, indent=2)
