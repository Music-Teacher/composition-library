import os
from libs.MusicLister import MusicLister
from libs.Composition import Composition
from libs.Helpers import Helpers
log = Helpers.log


class Actions:
  """
  This class contains static methods to perform actions requested by the HTTP server.
  """

  @staticmethod
  def refresh_database(composition_folder, database_file):
    if composition_folder and os.path.isdir(composition_folder):
      ml = MusicLister(composition_folder, database_file)
      ml.export_json()
      log(f"Database refreshed with composition folder '{composition_folder}'.")
      return True

    log(f"ERROR: Composition folder is not valid: '{composition_folder}'.")
    return False

  @staticmethod
  def create_info_file(als_file_path):
    info_file_path = Helpers.get_info_file_related_to_als(als_file_path)
    if not info_file_path:
      info_file_path = Helpers.get_info_file_name_from_als(als_file_path)
      try:
        with open(info_file_path, 'w') as info_file:
          for field in Composition.get_info_file_fields():
            info_file.write(f"{field}: \n")
        log(f"Info file created: '{info_file_path}'")
        return True

      except:
        pass
    log(f"ERROR: Could not create info file for ALS: '{als_file_path}'")
    return False
