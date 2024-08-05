// Receiver of Serial Messages from Raspberry Pi
  // always checking for new values on the serial port 
  // update the PWM output if so

// inputs over serial are 0 to 100
// convert to between 0 and 255 (PWM limits)


const int outputPin = 6; // Define the PWM output pin
int pwmVal = 0;
int intensity = 0;
String serial_data;

void setup() {

  pinMode(outputPin, OUTPUT); // Set the output pin as OUTPUT

  Serial.begin(9600); // Start serial communication

}

void loop() {
  
  // check for new intensity value of serial port (it comes as a string)
  if (Serial.available() > 0) {
    
    // read the incoming data
    serial_data = Serial.readStringUntil('\n');
    intensity = serial_data.toInt();

    // fix value within bounds if necessary
    if (intensity > 100) {
      intensity = 100;
    } else if (intensity < 0) {
      intensity = 0;
    }

    // convert intensity to PWM value
    pwmVal = map(intensity, 0, 100, 0, 255); // integer math only

  }

  // send PWM to pin
  analogWrite(outputPin, pwmVal);

  // delay in milliseconds (every 1 second run the loop)
  delay(1000);
  
}