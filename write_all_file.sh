process () (
  file_path=$1
  txt_file="${file_path/".als"/".txt"}"
  echo $txt_file
  if [[ -f $txt_file ]]; then
    echo "File found"
    cat "$txt_file"
  else
    echo "File not found, creating it"
    echo "$DEFAULT_TEXT" > "$txt_file"
  fi
)

export -f process

export DEFAULT_TEXT="""artist:
name:
album:
ep:
status:
chords:
lyrics:
extra_info:"""

find -maxdepth 2 -type f -name "*.als" -exec bash -c 'process "{}"' \; 
