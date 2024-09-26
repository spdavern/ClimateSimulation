## This script has no dependencies, purely to test sending intensity values over serial to Arduino

import time
import serial


COMM_PORT = "/dev/ttyACM0" # check this w/ `ls /dev/tty*` and plug/replug arduino
BAUD_RATE = 9600

try:
    ARDUINO = serial.Serial(port=COMM_PORT, baudrate=BAUD_RATE)
    IS_ARDUINO_SETUP = True

except Exception as e:
    print(f"Error was: {e}")
    ARDUINO = None
    IS_ARDUINO_SETUP = False

finally:
    if "ARDUINO" in locals() and ARDUINO and ARDUINO.is_open:
        ARDUINO.close()


for i in range(10):

    #on
    ARDUINO.write(str(int(100)) + "\n").encode("utf-8")
    time.sleep(1.5)
    
    #off
    ARDUINO.write(str(int(0)) + "\n").encode("utf-8")
    time.sleep(1.5)

