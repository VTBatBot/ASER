//BIST 2018 - 10/05/18
//Rotation_controller_code (v1.0 alpha)
//NSF experiment stepper motor driver code for arduino due. 
//Recieves input from PC via USBserial as instructions
//Outputs stepper motor controls

int ENA = 31;
int DIR = 33;
int PUL = 35;

void setup() {
//pin setup
pinMode(ENA, OUTPUT); // ENA: low - motor in free state, high - motor in control mode
pinMode(DIR, OUTPUT); // DIR: low - forwards, high - reverse
pinMode(PUL, OUTPUT); // PUL: pulse - once the driver sends a pulse, the motor moves a step
//initiate serial coms
SerialUSB.begin(9600);
digitalWrite(ENA, LOW);
digitalWrite(DIR, LOW);
digitalWrite(PUL, LOW);
}


void loop() {
  //Search for serial input
  if (SerialUSB.available() >= 1) {  //serial input found
      SerialUSB.read();
      SerialUSB.read(); // clear buffer of 2 bytes from MATLAB.
      //Forward 1 degree
      digitalWrite(PUL,HIGH);
      delayMicroseconds(10);
      digitalWrite(PUL,LOW);
      delayMicroseconds(10);
  }
}
