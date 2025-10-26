import os
import json

from libs.Composition import Composition
from libs.Helpers import Helpers

log = Helpers.log

class MusicLister:
  """
  MusicLister is the main class to list compositions.
  This class will look for compositions in the root_folder path.
  It can export the list of compositions to a JSON file.

  So far, it supports Ableton Live Sets (.als) only.
  ALS files are searched recursively in the given root folder.
  They must not be in subfolders containing other ALS files.
  """

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
