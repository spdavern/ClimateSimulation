#!/bin/bash

SESSION_NAME="web_app"
VENV_PATH="~/pond_venv"
WEBAPP_FOLDER="~/ClimateSimulation/"
PYTHON_SCRIPT="rpi/climate_web_interface.py"

echo "Checking for exising $SESSION_NAME session."
if [[ -n $(tmux ls | grep web_app) ]]; then
    echo "Killing existing $SESSION_NAME session."
    tmux kill-session -t $SESSION_NAME
fi
echo "Running new $SESSION_NAME session."
# create new tmux session, source venv, run python script
tmux new-session -d -s $SESSION_NAME "source $VENV_PATH/bin/activate && cd $WEBAPP_FOLDER && python3 $PYTHON_SCRIPT"
tmux ls | grep web_app
