#!/bin/bash

SESSION_NAME="web_app"

VENV_PATH="~/pond_venv"

PYTHON_SCRIPT="~/ClimateSimulation/rpi/climate_web_interface.py"

# create new tmux session, source venv, run python script
tmux new-session -d -s $SESSION_NAME "source $VENV_PATH/bin/activate && usr/bin/python3 $PYTHON_SCRIPT"


