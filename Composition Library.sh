HOME=$PWD

other_commands() {
  tput setaf 1
  printf "\rSIGINT caught"
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

log_step() { echo -e "\n\e[42m# $*\e[0m\n"; }

# Start python backend
cd python-back
log_step "Starting Python Backend"
mkdir -p logs
python music_lister.py ../database/database.json > logs/music_lister.log 2>&1 &
PYTHON_BACK_PID=$(echo $!)
cd $HOME

# Start backend
cd back
log_step "Starting Express Backend"
rm -rf node_modules
npm i --package-lock-only --omit=dev
npm ci --omit=dev
mkdir -p logs
node server.js > logs/express-backend.log 2>&1 &
BACKEND_PID=$(echo $!)
cd $HOME

# Start frontend
cd front
log_step "Starting Vue Frontend"
rm -rf node_modules
npm i --package-lock-only --omit=dev
npm ci --omit=dev
mkdir -p logs
npm run dev
FRONTEND_PID=$(echo $!)
cd $HOME
