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

Open a terminal and connect to the Raspberry Pi (`ssh pond@<ip_address>`) which will be on the PNNL Devices network which is accessible from the Lab network you must be VPN'd into. Alternately, use VSCode and the Remote Explorer extension to connect to the RPi.

### Setup (first time)

open a terminal  
`ssh pond@<ip_address>` # No port here. Provide PW.  
`sudo apt-get update`  
`sudo apt-get install tmux`  

Set the RaspberryPi's given hostname: (defaults to raspberrypi)
`sudo hostnamectl set-hostname <Given_Name>`  
Consider installing iTerm2 Shell Integration so that the hostname is displayed in the terminal window. (iTerm2 > Install Shell Integration)

Clone the repo into the pond user's home folder:  
`cd ~`  
`git pull https://github.com/philparisi/climatesimulation`  
If you're doing development on a particular RPi, you might want to update the developer username and email: `git config --global user.name "User Name"` and `git config --global user.email "user_email@pnnl.gov"`. This should enable pushing changes back to github.

make a virtual environment  
`cd ~/ClimateSimulation`  
`python3 -m venv pond_venv`  
`source pond_venv/bin/activate`  

install dependencies  
`pip install -e .`

### RPi - Running Web App

#### Single command to start the web app:
`cd ~/ClimateSimulation`  
`./reboot_climate_web_app.sh`  
This should start a tmux session named 'web_app' and start the web app: a python Flask app. If the tmux session does not persist (`tmux ls`) or the web app is not accessible via a browser, something happened. If the tmux session is still alive, attach to it (`tmux a` or `tmux a -t web_app`) and observe the logs. There should be error messages. If the tmux session does not persist run the program manually (below) and observe issues.

#### Manually run the web app:  
`tmux new -s web_app`  # Doing the steps below in a tmux session is optional, as is naming the session.  
`cd ~/ClimateSimulation`  
`source pond_venv/bin/activate`  
`python3 rpi/climate_web_interface.py`  
check the output for the ip address!

(note recommend) the below will only use the default `127.0.0.1:5000`  
`flask --app <file> run`

find the Web GUI by opening a web browser and going to:
<ip_address>:<port>

### Observing Web App Logs - Live Troubleshooting

The web app logs many activities it performs to the session (e.g. tmux) it is started in. Those logs currently only persist in the tmux session which has a limited length. Older log content is discarded by tmux. So, ssh'ing into a Rpi and attaching to a live ClimateSimulation tmux session (`tmux a` or `tmux a -t web_app`) will enable one to observe the available logs. You may need to switch to tmux's copy mode `Ctrl+b [` to scroll. Use `q` to quit copy mode.

Use `Ctrl+c` to kill the flask app.  
Use `Ctrl+b d` to detach from the running tmux session.

## Climate Simulation Flow

### Web App

The web app is responsible for allowing users to:
- view the current status of the climate simulation
- upload a new light profile and run it

When a light profile is run a separate Light Controller process is started that both sends instructions to the Arduino and updates a climate_config.json. This json enables restarting of a light profile if the system goes down and critical communication between the web app and the Light Controller process.

Handoff with Light Controller:  
- A 'handoff' occurs by placing the user's uploaded light profile file into `/rpi/static/live/<file.ext>` for use during the profile's lifetime.   
- A ClimateConfig object that lives within the web app creates the `/rpi/static/live/live_plot.png`, when needed, that the web app will show by the View 'Live' Profile page.

### Light Controller:

The Light Controller process is instantiated (by the web app) with content in the `/rpi/static/live` folder and is responsible for progressing through the times/intensities in the profile it is instantiated with. When it is time to send a new intensity to the lights, it sends the intensity to the Arduino over a serial USB cable.  

### Arduino Script
The arduino script waits for new values to be sent over the serial USB from the RPi. It receives a value, and sends it using PWM to the lights until told otherwise.  

Electronics:
- the arduino can send 0-5V by default on PWM pins
- an added voltage multiplier doubles the arduino voltage (sends 0-10V) to lights
