#!/bin/bash

music_lister_kill() {
  tput setaf 1
  printf "\rSIGINT caught      "
  tput sgr0
  sleep 1

  if [[ ! -z "$MUSIC_LISTER_ID" ]]; then
      printf "\nStopping python backend (PID $MUSIC_LISTER_ID)... "
      kill -SIGTERM $MUSIC_LISTER_ID
      wait $MUSIC_LISTER_ID 2>/dev/null
      printf "Done.\n"
  fi
  
  printf "Exiting program.\n"
  exit 0
}
trap 'music_lister_kill' SIGTERM SIGINT

# Documentation if script misused
usage () (
program_name="$0"
if [ ! $# -eq 0 ]; then
  program_name="./"$1
fi
cat << EOF
Usage: 
  $program_name
EOF
)

# Check input parameters
if [[ "${BASH_SOURCE[0]}" != "${0}" ]];then
  echo "Script must be executed, not sourced."
  usage ${BASH_SOURCE[0]}
  return
fi

# Start program
echo "Checking dependencies..."
if [[ ! -d "venv" ]]; then
  python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

echo "Launching music_lister program..."
python music_lister.py &
MUSIC_LISTER_ID=$(echo $!)
echo "Music lister started with PID $MUSIC_LISTER_ID."
deactivate

# Keep alive
while /bin/true; do
  sleep 2
done
