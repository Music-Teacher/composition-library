import os
import re
import sys
import threading
import time
from html5builder import HTML5Builder

# USER PARAMETERS
# Set the folder to search
COMPOSITIONS_FOLDER="/mnt/c/Users/obrun/Music/Compositions"
#####

# Current script path
CURRENT_SCRIPT_PATH=os.path.dirname(os.path.realpath(__file__))
DESIGN_FILE_PATH=os.path.join(CURRENT_SCRIPT_PATH, "design.css")

# Timeout and update frequency
APP_TIMEOUT = 60*60 # 1 hour
UPDATE_FREQUENCY = 20 # 20 seconds

class Composition:
  """This class will hold the composition information.
  It will look for an info file on disk, based on the ALS file path given."""

  name = None
  artist = None
  lyrics = None
  extra_info = None
  status = None
  rework = None

  als_file_path = None
  project_dir = None
  root_folder = None
  als_file_name = None

  def __init__(self, als_file_path, root_folder=None):
    self.als_file_path = als_file_path
    self.root_folder = root_folder
    self.project_dir = os.path.dirname(als_file_path)
    self.als_file_name = os.path.basename(als_file_path)
    self.gather_composition_information()

  def gather_composition_information(self):
    info_file_path = Helpers.get_info_file_related_to_als(self.als_file_path)
    if info_file_path:
      info = Helpers.get_fields_from_file(info_file_path)
      self.name = info.get("name", self.als_file_name) or self.als_file_name
      self.artist = info.get("artist", None) or None
      self.lyrics = info.get("lyrics", None) or None
      self.extra_info = info.get("extra_info", None) or None
      self.chords = info.get("chords", None) or None
      self.status = info.get("status", None) or None
    self.make_proper_status()
  
  def make_proper_status(self):
    if Helpers.is_status_complete(self.status):
      self.status = "Finished"
    else:
      self.rework = self.status
      self.status = "In Progress"

  def __str__(self):
    return_string = f"# {self.artist+" - " if self.artist else ""}{self.name}\n"
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
    return return_string

  def __html__(self):
    tag = HTML5Builder()
    list_of_elements = []

    list_of_elements.append(tag.h2(f"{self.artist+" - " if self.artist else ""}{self.name}"))

    list_of_elements.append(tag.p(f"Status: {self.status}", cls="status"))
    if self.rework:
      list_of_elements.append(tag.p(f"Rework: {self.rework}", cls="rework"))

    path_to_display = self.als_file_path
    if self.root_folder:
      path_to_display = os.path.relpath(self.als_file_path,self.root_folder)
    list_of_elements.append(tag.p(f"File path: {str(tag.span(path_to_display, cls="file_path"))}", cls="als_file_path"))

    row1 = tag.tr([tag.th("Lyrics"), tag.th("Extra info"), tag.th("Chords")])
    row2 = tag.tr([tag.td(self.lyrics), tag.td(self.chords), tag.td(self.extra_info)])
    summary = tag.summary("More info")
    list_of_elements.append(tag.details([summary, tag.table([row1, row2], border="0", cellpadding="5")]))
    
    composition_div_classes = "composition"
    if Helpers.is_status_complete(self.status):
      composition_div_classes += " finished"
    else:
      composition_div_classes += " unfinished"
    total_div = tag.div(list_of_elements, cls=composition_div_classes)

    return str(total_div)


class MusicLister:
  """This class will look for Ableton Live Sets.
  It will find them in the root_folder path."""

  root_folder = None
  output_html_file = None
  compositions = dict()

  def __init__(self, root_folder):
    assert os.path.isdir(root_folder)
    self.root_folder = root_folder
    self.output_html_file = os.path.join(root_folder, "index.html")
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

  def export(self, silent=False):
    if not silent:
      print(f"Exporting HTML library to: {self.output_html_file}")
    file = open(self.output_html_file, 'w')
    file.write(self.__html__())
    file.close()
  
  def __str__(self):
    return_string = f"\n###################\nRoot folder: {self.root_folder}\n"
    return_string += f"Output HTML file: {self.output_html_file}\n"
    return_string += f"Number of compositions: {len(self.compositions)}\n"
    # return_string += "\n"
    # for name in self.compositions:
    #   return_string += f"{self.compositions[name]}"
    return_string += f"###################"
    return return_string

  def __html__(self):
    tag = HTML5Builder()
    title = tag.title(f"Music Lister - {os.path.basename(self.root_folder)}")
    css = tag.link(href=Helpers.replace_wsl_disk_with_windows(DESIGN_FILE_PATH), rel="stylesheet")
    meta = tag.meta(charset="UTF-8")
    head = tag.head([title, css, meta])

    main_title = tag.h1(title)

    summary = tag.summary("About this list")
    detail1 = tag.li(f"Root folder: {tag.span(Helpers.replace_wsl_disk_with_windows(self.root_folder), cls="file_path")}")
    detail2 = tag.li(f"Output HTML file: {tag.span(Helpers.replace_wsl_disk_with_windows(self.output_html_file), cls="file_path")}")
    detail3 = tag.li(f"Number of compositions: {len(self.compositions)}")
    details_list = tag.ul([detail1, detail2, detail3])
    details = tag.div(tag.details([summary, details_list]), cls="lister_details")

    compositions = tag.div('', cls="compositions")
    for name in self.compositions:
      compositions.child.append(self.compositions[name].__html__())

    body = tag.body([main_title, details, compositions])

    doc = tag.html([head, body], lang='html')
    return str(tag.doctype + str(doc))
    

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
  def get_fields_from_file(path):
    fields = dict()
    with open(path) as file:
      for line in file:
        line = line.rstrip()
        try:
          key, value = line.split(':', 1)
          fields[key] = value
        except:
          #ignoring line
          pass
    return fields

  @staticmethod
  def is_status_complete(status):
    if status in ["finished", "Finished", "FINISHED", "Complete"]:
      return True
    return False
  
  @staticmethod
  def replace_wsl_disk_with_windows(path):
    return re.sub(r'/mnt/([a-z]{1})', r'\1:', path)


# Main code
def main_code(silent=False):
  ml = MusicLister(COMPOSITIONS_FOLDER)
  ml.export(silent)

def main_thread(frequency):
  while True:
    if e.is_set():
      break
    main_code(silent=True)
    time.sleep(frequency)

if __name__ == "__main__":
  if not (len(sys.argv) >= 1 and sys.argv[1] in ['once', 'periodically']):
    print("Usage:")
    print("  python music_lister.py once|periodically")
    print("  Options:")
    print("    once: Run the program once")
    print("    periodically: Run the program periodically in the background")
    sys.exit(2)

  print("Starting music_lister...")
  if sys.argv[1] == "once":
    main_code()
  elif sys.argv[1] == "periodically":
    main_thread = threading.Thread(target=main_thread, args=(UPDATE_FREQUENCY,))
    e = threading.Event()
    main_thread.start()
    print(f"Program running periodically with timeout {APP_TIMEOUT}s and frequency {UPDATE_FREQUENCY}s.")
    main_thread.join(APP_TIMEOUT)
    e.set()
    main_thread.join()
