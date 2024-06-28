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
`source pond_venv/bin/activate`  

install dependencies  
`cd ClimateSimulation`  
`python install -e .`  ß

### RPi - Running Web App

source venv  
`source pond_venv/bin/activate`  

manually run program  
`cd ClimateSimulation/rpi`   
`python3 climate_web_interface.py`  
check the output for the ip address!

(note recommend) the below will only use the default `127.0.0.1:5000`  
`flask --app <file> run`

find the Web GUI by opening a web browser and going to:
<ip_address>:<port>

## Climate Simulation Flow

### Web App
The web app is responsible for allowing users to:
- view the current status of the climate simulation
- upload a new light profile and run it

Handoff with Python Serial Manager:  
- A 'handoff' occurs by placing the user's uploaded light profile file into `/rpi/static/live/<file.ext>` for the python serial manager.   
- The python serial manager creates the `/rpi/static/live/live_plot.png` that the web app will show on the View 'Live' Profile page.

### Python Serial Manager
The python serial manager is always checking the `/rpi/static/live` folder and is responsible for taking any newly uploaded light profiles (thru the web app) and progressing going through the times/intensities.  

When it is time to send a new intensity to the lights, it:
- sends the intensity to the Arduino over a serial USB cable.  
- creates a new `/rpi/static/live/live_plot.png` for the web app to display

### Arduino Script
The arduino script waits for new values to be sent over the serial USB from the RPi. It receives a value, and sends it using PWM to the lights until told otherwise.  

Electronics:
- the arduino can 0-5V by default on PWM pins
- an added voltage multiplier doubles the arduino voltage (sends 0-10V) to lights
