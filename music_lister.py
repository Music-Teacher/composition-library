import os
from html5builder import HTML5Builder

COMPOSITIONS_FOLDER="/mnt/c/Users/obrun/Music/Compositions"


class Composition:
  name = None
  artist = None
  lyrics = None
  extra_info = None
  status = None
  rework = None

  als_file_path = None
  project_dir = None

  def __init__(self, als_file_path):
    self.als_file_path = als_file_path
    self.project_dir = os.path.dirname(als_file_path)
    self.name = os.path.basename(als_file_path)
    self.gather_composition_information()

  def gather_composition_information(self):
    info_file_path = Helpers.get_info_file_related_to_als(self.als_file_path)
    if info_file_path:
      info = Helpers.get_fields_from_file(info_file_path)
      self.name = info.get("name", None)
      self.artist = info.get("artist", None)
      self.lyrics = info.get("lyrics", None)
      self.extra_info = info.get("extra_info", None)
      self.status = info.get("status", None)
    self.make_proper_status()
  
  def make_proper_status(self):
    if Helpers.is_status_complete(self.status):
      self.status = "Finished"
    else:
      self.rework = self.status
      self.status = "Not finished"

  def __str__(self):
    return_string = f"# {self.artist+" - " if self.artist else ""}{self.name}\n"
    return_string += f" + Status: {self.status}\n"
    if self.rework:
      return_string += f" + Rework: {self.rework}\n"
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
    list_of_elements.append(tag.p(f"File path: {self.als_file_path}", cls="als_file_path"))

    list_of_elements.append(tag.p(f"Status: {self.status}", cls="status"))
    if self.rework:
      list_of_elements.append(tag.p(f"Rework: {self.rework}", cls="rework"))

    row1 = tag.tr([tag.th("Lyrics"), tag.th("Extra info")])
    row2 = tag.tr([tag.td(self.lyrics), tag.th(self.extra_info)])
    list_of_elements.append(tag.table([row1, row2], border="0", cellpadding="5"))
    
    composition_div_classes = ["composition"]
    if Helpers.is_status_complete(self.status):
      composition_div_classes.append("finished")
    else:
      composition_div_classes.append("unfinished")
    total_div = tag.div(list_of_elements, cls=composition_div_classes)

    return str(total_div)


class MusicLister:
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
      self.compositions[path] = Composition(path)
    
    if os.path.isfile(path):
      return

    als_present = Helpers.is_als_present_in_path(path)

    for element in os.listdir(path):
      next_path = os.path.join(path, element)
      if als_present and os.path.isdir(next_path):
        continue
      self.look_for_als(next_path)

  def export(self):
    print(f"Exporting to: {self.output_html_file}")
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
    title = f"Music Lister - {os.path.basename(self.root_folder)}"
    head = tag.head(tag.title(title))

    main_title = tag.h1(title)
    detail1 = tag.li(f"Root folder: {self.root_folder}")
    detail2 = tag.li(f"Output HTML file: {self.output_html_file}")
    detail3 = tag.li(f"Number of compositions: {len(self.compositions)}")
    details = tag.div([tag.ul([detail1, detail2, detail3])], cls="lister_details")

    compositions = tag.div('', cls="compositions")
    for name in self.compositions:
      compositions.child.append(self.compositions[name].__html__())

    body = tag.body([main_title, details, compositions])

    doc = tag.html([head, body], lang='html')
    return str(tag.doctype + str(doc))
    


class Helpers:
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


# Launch main code
if __name__ == "__main__":
  ml = MusicLister(COMPOSITIONS_FOLDER)
  ml.export()
