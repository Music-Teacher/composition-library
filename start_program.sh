HOME=$PWD

other_commands() {
  tput setaf 1
  printf "\rSIGINT caught      "
  tput sgr0
  sleep 1

  if [[ ! -z "$PYTHON_BACK_PID" ]]; then
      printf "\nStopping python backend (PID $PYTHON_BACK_PID)... "
      kill -SIGTERM $PYTHON_BACK_PID
      wait $PYTHON_BACK_PID 2>/dev/null
      printf "Done.\n"
  fi

  if [[ ! -z "$BACKEND_PID" ]]; then
      printf "Stopping backend (PID $BACKEND_PID)... "
      kill -SIGTERM $BACKEND_PID
      wait $BACKEND_PID 2>/dev/null
      printf "Done.\n"
  fi

  if [[ ! -z "$FRONTEND_PID" ]]; then
      printf "Stopping frontend (PID $FRONTEND_PID)... "
      kill -SIGTERM $FRONTEND_PID
      wait $FRONTEND_PID 2>/dev/null
      printf "Done.\n"
  fi

  printf "Exiting program.\n"
  exit 0
}
trap 'other_commands' SIGINT

# Start python backend
cd python-back
mkdir -p logs
echo "Checking dependencies..."
if [[ ! -d "venv" ]]; then
  python -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
python music_lister.py > logs/music_lister.log 2>&1 &
PYTHON_BACK_PID=$(echo $!)
deactivate
cd $HOME

# Start backend
cd back
npm install
mkdir -p logs
node server.js > logs/express-backend.log 2>&1 &
BACKEND_PID=$(echo $!)
cd $HOME

# Start frontend
cd front
npm install
npm run dev
FRONTEND_PID=$(echo $!)
cd $HOME
