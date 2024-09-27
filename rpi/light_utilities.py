# functions for the lights undergoing climate simulation
# check device port depending on your system (/dev/ttyACM0 and /dev/ttyACM1 are common)
# viewable in Arduino IDE or `ls /dev/tty*`, set baudrate in IDE

import logging
import os
import time
import serial

# TODO: COMM_PORT should probably come by detection in the os or by a system variable that
# can be set up by the reboot_climate_web_app.sh.
COMM_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# class Arduino:
#     """A dummy Arduino class to facilitate testing.

#     To use uncomment this class, comment out the `ARDUINO = serial.Serial...` line below,
#     and uncomment the `ARDUINO = Arduino()` line below that.
#     """

#     def __init__(self) -> None:
#         self.is_open = True

#     def write(self, message):
#         print(f"Sent to Arduino: {message}")


try:
    ARDUINO = serial.Serial(port=COMM_PORT, baudrate=BAUD_RATE)
    # ARDUINO = Arduino()
    IS_ARDUINO_SETUP = True

except Exception as e:
    print(f"Error was: {e}")
    ARDUINO = None
    IS_ARDUINO_SETUP = False


def flash_lights_thrice(arduino=ARDUINO):
    """Used to inform user of a successful action by flashing pond lights 3x

    Arguments:
        arduino(serial object): Serial object for the Arduino controlling the lights.

    Returns:
        None
        Physically flashes the lights 3 times.
    """

    for i in range(3):
        logger.info("Flash light...%s", arduino)
        send_to_arduino(100, arduino)
        time.sleep(0.5)
        send_to_arduino(0, arduino)
        time.sleep(0.5)
    return


def send_to_arduino(val, arduino=ARDUINO):
    """Sends a value to the Arduino to control the lights

    Arguments:
        arduino(serial object): Serial object for the Arduino controlling the lights.
        val(float): Value to send to the Arduino, cast this as int

    Returns:
        None
        Sends the value to the Arduino.
    """
    if IS_ARDUINO_SETUP:
        arduino.write(bytes(f"{val}\n", "utf-8"))
    return


if ARDUINO and ARDUINO.is_open:
    flash_lights_thrice()
