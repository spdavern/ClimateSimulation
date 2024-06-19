# ClimateSimulation
Algae Pond Lighting Climate Simulation


## For Users

1. connect your laptop to any lab-based network (if you are remote, connect thru VPN)
2. open a web browser and go to `<ip_address>:5000`
3. read instructions on web site
4. upload excel file that contains light profile
5. select appropriate settings
5. send it to the RPi, program will start running!
6. return to the site to watch the progress throughout the cycle, or upload a new light profile


## For Developers


### Setup (first time)

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

### RPi - Running Web App

source venv
`source pond_venv/bin/activate`

run program
`cd ClimateSimulation/src/climatesimulation/rpi/web`
`python3 <file.py>`

the below will only use the default `127.0.0.1:5000`
`flask --app <file> run`

find the Web GUI by opening a web browser and going to:
<ip_address>:<port>

#### trigger


### Arduino - Sending Voltages

arduino sends 0-5V by default on PWM pins
voltage multiplier doubles the arduino voltage (sends 0-10V) to Vivosun lights
