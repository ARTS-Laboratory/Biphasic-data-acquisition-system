#include "Arduino.h"

const int in1 = 0;
const int in2 = 1;
int frequency = 10; // in Hz
int dutyCycle = 50; 

int period = 1000 / frequency;
int onTime = (period * dutyCycle) / 100;
int offTime = period - onTime;

int main()
{
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  Serial.begin(9600);

  while(1)
  {
    digitalWrite(in2, LOW);
    digitalWrite(in1, HIGH);
    delay(onTime);

    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    delay(onTime);
  }
  
  return 0;
}
