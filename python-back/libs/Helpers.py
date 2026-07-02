import os
import datetime
import re
import glob


class Helpers:
  """
  Helpers is a static class containing helper functions for this project.
  - is_als: Check if a given path is an ALS file.
  - is_als_present_in_path: Check if an ALS file is present in a given directory.
  - get_info_file_related_to_als: Get the info file path related to a given ALS file.
  - get_info_file_name_from_als: Get the expected info file name from a given ALS file.
  - is_expected_file: Check if a file has one of the expected extensions.
  - get_audio_files_related_to_als: Get audio files related to a given ALS file.
  - get_cover_art: Get cover art image related to a given ALS file.
  - get_fields_from_file: Extract fields from an info file.
  - is_status_complete: Check if a status string indicates completion.
  - get_all_project_items: Get all project item paths related to a given ALS file.
  - get_project_name_from_als: Get the project name from a given ALS file.
  - get_file_extension: Get the file extension from a file path.
  - remove_file_extension: Retuen the file without its extension if any.
  - get_renamed_item_path: Get the new path for a renamed project item.
  - log: Log a message with a timestamp.
  """

  def __new__(cls):
    raise TypeError('Class Helpers is static and cannot be instantiated.')

  @staticmethod
  def is_als(path):
    return Helpers.is_expected_file(path, ["als"])

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
  def get_info_file_related_to_als(als_file_path):
    file_path = Helpers.get_info_file_name_from_als(als_file_path)
    if os.path.isfile(file_path):
      return file_path
    return None

  @staticmethod
  def get_info_file_name_from_als(als_file_path):
    if Helpers.is_als(als_file_path):
      return als_file_path.replace(".als", ".txt")
    return None
  
  @staticmethod
  def is_expected_file(file_path, list_of_extensions):
    if os.path.isfile(file_path) and list_of_extensions:
      file_name = os.path.basename(file_path)
      extension = Helpers.get_file_extension(file_path)
      if extension and extension.lower() in [ext.lower() for ext in list_of_extensions]:
        return True
    return False

  @staticmethod
  def get_all_files_in_dir_sorted_by_date_desc(dir_path):
    files = list(filter(os.path.isfile, glob.glob(dir_path + "/*")))
    files.sort(key=lambda x: os.path.getmtime(x))
    files.reverse()
    return files

  @staticmethod
  def get_audio_files_related_to_als(als_file_path):
    audio_files = []
    als_dir = os.path.dirname(als_file_path)
    for file in Helpers.get_all_files_in_dir_sorted_by_date_desc(als_dir):
      if Helpers.is_expected_file(file, ["mp3", "wav", "ogg"]):
        audio_files.append(os.path.join(als_dir, file))
    return audio_files

  @staticmethod
  def get_cover_art(als_file_path):
    als_dir = os.path.dirname(als_file_path)
    extensions = ["jpg", "jpeg", "png"]
    for ext in extensions:
      print(ext)
      test_cover = Helpers.remove_file_extension(als_file_path)+"."+ext
      print(test_cover)
      if os.path.isfile(test_cover):
        return test_cover
    for file in Helpers.get_all_files_in_dir_sorted_by_date_desc(als_dir):
      if Helpers.is_expected_file(file, extensions):
        return os.path.join(als_dir, file)
    return None

  @staticmethod
  def get_fields_from_file(path, fields_to_extract):
    fields = dict()

    def save_field(field_name, field_value):
      if field_name and field_value:
        fields[field_name.strip()] = field_value.strip()

    with open(path) as file:
      field_name = field_value = None
      # Parse file line by line
      for line in file:
        line = line.strip()

        # Check if new field
        try:
          key, value = line.split(':', 1)
        except:
          key = value = None
        if key and key.lower().strip() in fields_to_extract:

          # If new key, save previous one with its value
          save_field(field_name, field_value)
          field_name = key
          field_value = value
        elif field_name:

          # If no new key, append line to previous value
          field_value += f"\n{line}"
      # Save last field
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
  def get_project_name_from_als(als_file_path):
    if Helpers.is_als(als_file_path):
      return os.path.basename(als_file_path).replace(".als", "")
    return None
  
  @staticmethod
  def get_all_project_items(als_file_path):
    if not Helpers.is_als(als_file_path):
      return []
    list_of_elements = [als_file_path]
    list_of_elements.append(Helpers.get_info_file_name_from_als(als_file_path))
    # Project folder must be included last
    list_of_elements.append(os.path.dirname(als_file_path))
    return list_of_elements
  
  @staticmethod
  def get_file_extension(file_path):
    if os.path.isfile(file_path) and '.' in os.path.basename(file_path):
      return os.path.basename(file_path).split('.')[-1]
    return ''
  
  @staticmethod
  def remove_file_extension(file_path):
    if os.path.isfile(file_path) and '.' in os.path.basename(file_path):
      split_file_path = file_path.split('.')
      split_file_path.pop()
      return ".".join(split_file_path)
    return file_path
  
  @staticmethod
  def get_renamed_item_path(original_file_path, project_name, new_base_name):
    item_path = os.path.dirname(original_file_path)
    item_name = os.path.basename(original_file_path)
    new_item_name = item_name.replace(project_name, new_base_name)
    new_full_path = os.path.join(item_path, new_item_name)
    return new_full_path

  @staticmethod
  def log(message):
    print(f"[{datetime.datetime.now()}] {message}", flush=True)

log = Helpers.log
