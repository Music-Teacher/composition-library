# This is a simple music lister for Ableton program

This program takes as parameter the folder path where your Ableton compositions are.
It will then generate an HTML file in this folder, called index.html, containing all your compositions.

You can open the index.html file with your favourite browser.

Keep in mind that:
- Folder path must be set inside music_lister.py, top of the file
- Each als file must have a .txt file with the same name next to it
  - Example: Compo1.als --> Compo1.txt
- The text file must have the following content:
```
artist: Me
name: The Flower
album:
status:
Voice needs to be recorded again
Guitar is not loud enough
lyrics:
extra_info:
chords: (barred) G C Am F
```
  - If status is set to Finished or Complete, it will be considered Finished. Any other text will be considered in "To Rework" state
- If a wav file is exported next to txt and als files, with same name, it will be listenable directly on the HTML page
