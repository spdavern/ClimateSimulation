# ClimateSimulation
algae pond climate simulation


## Setup (first time)

open a terminal
`sudo apt-get install tmux`

pull repo
`cd`
`git pull https://github.com/philparisi/climatesimulation` 

make a virtual environment
`python3 -m venv pond_venv`
`cd ClimateSimulation`
`source pond_venv/bin/activate`

install dependencies
`python install -e .`

## RPi - Running Web App

source venv and run app
`source pond_venv/bin/activate`
`cd ClimateSimulation`
`flask

### trigger


## Arduino - Sending Voltages

arduino sends 0-5V by default on PWM pins
voltage multiplier doubles the arduino voltage (sends 0-10V) to Vivosun lights
