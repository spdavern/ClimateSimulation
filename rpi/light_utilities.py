# functions for the lights undergoing climate simulation
import time
import serial

COMM_PORT = "/dev/ttyACM0"
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


def flash_lights_thrice(arduino=ARDUINO):
    """Used to inform user of a successful action by flashing pond lights 3x

    Arguments:
        arduino(serial object): Serial object for the Arduino controlling the lights.

    Returns:
        None
        Physically flashes the lights 3 times.
    """

    for i in range(3):

        send_to_arduino(arduino, 100)
        time.sleep(1.5)
        send_to_arduino(arduino, 0)
        time.sleep(1.5)

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
        arduino.write(str(int(val)) + "\n").encode("utf-8")

    return
