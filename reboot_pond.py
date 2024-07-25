import os
import subprocess

command = f"tmux new-session -d -s web2 'source /home/pond/pond_venv/bin/activate && python3 /home/pond/ClimateSimulation/rpi/climate_web_interface.py'"

print(command)

try:
	result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)

except Exception as e:

	print("uhhh", str(e))

print("stdout:", result.stdout)
print("stderr:", result.stderr)
