// Simple Light Test Script for Arduino to send 0 to 5V
  // booster circuit sends 0 to 10V to the light
  // cutin voltage is ~1.8V for Vivosun lights to start

const int outputPin = 6; // Define the output pin
int voltageLevel = 850; // Start at 0V
int increment = 250; // Voltage increment mV step PWM (0 to 255)
  // 500 (0.5V), 1000 (1V), 1500 (1.5V) and so on

int pwmVal;

void setup() {
  pinMode(outputPin, OUTPUT); // Set the output pin as OUTPUT
}

void loop() {
  
  // convert voltage level to PWM value
  pwmVal = map(voltageLevel, 0, 5000, 0, 255);

  // send PWM to pin
  analogWrite(outputPin, pwmVal);

  // increment voltage level for next time
  //voltageLevel += increment;

  if (voltageLevel > 5000) {
    voltageLevel = 0;
  }

  // delay in milliseconds
  delay(1000);
}


