## This script has no dependencies, purely to test sending intensity values over serial to Arduino
    # be sure to send the \n new line character, as the arduino expects this
    
import time
import serial

# check device port depending on your system (/dev/ttyACM0 and /dev/ttyACM1 are common for RPi)
    # viewable in Arduino IDE or `ls /dev/tty*`, set baudrate in IDE
#COMM_PORT = "/dev/cu.usbmodem1101" 
COMM_PORT = "/dev/ttyACMO"
BAUD_RATE = 9600

try:
    ARDUINO = serial.Serial(port=COMM_PORT, baudrate=BAUD_RATE)
    IS_ARDUINO_SETUP = True

except Exception as e:
    print(f"Error was: {e}")
    ARDUINO = None
    IS_ARDUINO_SETUP = False


if IS_ARDUINO_SETUP:
    
    # flash lights thrice
    for i in range(4):

        #on
        ARDUINO.write(bytes(f"{100}\n",'utf-8'))
        time.sleep(0.5)
    
        #off
        ARDUINO.write(bytes(f"{0}\n",'utf-8'))
        time.sleep(0.5)


    # ramp up and down (don't hate me for hard coding this)
    time.sleep(2)
    ARDUINO.write(bytes(f"{20}\n",'utf-8'))
      
    time.sleep(0.5)
    ARDUINO.write(bytes(f"{35}\n",'utf-8'))
    
    time.sleep(0.5)
    ARDUINO.write(bytes(f"{50}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{65}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{80}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{100}\n",'utf-8'))    
    
    time.sleep(0.5)
    ARDUINO.write(bytes(f"{80}\n",'utf-8'))    
    
    time.sleep(0.5)
    ARDUINO.write(bytes(f"{65}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{50}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{35}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{20}\n",'utf-8'))

    time.sleep(0.5)
    ARDUINO.write(bytes(f"{0}\n",'utf-8'))