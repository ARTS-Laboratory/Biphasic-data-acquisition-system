#include "Arduino.h"
#include "TeensyTimerTool.h"
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_ADS1X15.h>
#include "xparameters.h"

using namespace TeensyTimerTool;
Adafruit_ADS1115 ads;
OneShotTimer timer1;
OneShotTimer adcTimer;

int frequency = 50;                       // in Hz
bool toggleState = false;
int period = 1000 / frequency;            // period in milliseconds
int halfPeriod = period / 2;              // half period for 50% duty cycle
int adcDelay = halfPeriod * 0.8;          // 80% of half period
float in_line = 680000;                   // value of known resistor
const float multiplier = 0.1875F;         // for 16 bit dac @ +/-6.144V gain
char buffer[64]; 
char resistance_str[16];

const unsigned long SamplePeriod = 1000;  // sampling period in milliseconds

uint8_t readDIPSwitches() {
  digitalWrite(LATCH_PIN, LOW);  // Pulse the latch pin to load the parallel data
  delayMicroseconds(5);
  digitalWrite(LATCH_PIN, HIGH);
  
  uint8_t switchState = 0;
  for (int i = 0; i < 8; i++) {
    switchState |= (digitalRead(DATA_PIN) << i); // Read each bit
    digitalWrite(CLOCK_PIN, HIGH); // Pulse the clock to shift the next bit
    delayMicroseconds(5);
    digitalWrite(CLOCK_PIN, LOW);
  }
  
  return switchState;
}

void togglePins()
{
    if (toggleState)
    {
			  CORE_PIN0_PORTSET = CORE_PIN0_BITMASK;
			  CORE_PIN1_PORTCLEAR = CORE_PIN1_BITMASK;
        adcTimer.trigger(adcDelay * 1000); // convert to microseconds
    }
    else
    {
			  CORE_PIN0_PORTCLEAR = CORE_PIN0_BITMASK;
			  CORE_PIN1_PORTSET = CORE_PIN1_BITMASK;
    }
    toggleState = !toggleState;

    timer1.trigger(halfPeriod * 1000);    // restart the main timer for the next toggle
}

void readADC() 
{
//   int16_t val_drop = ads.readADC_Differential_2_3();  
//   int16_t val_sense = ads.readADC_Differential_0_1();

  float r = bigR(100.0, 100.0, 1000.0);

  dtostrf(r, 6, 3, resistance_str);
  snprintf(buffer, sizeof(buffer), "%s", resistance_str);
  Serial.println(buffer);
}

int main() 
{
  Serial.begin(9600);
  
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(DATA_PIN, INPUT);

  uint8_t switchState = readDIPSwitches();
  
  for (int i = 0; i < 8; i++) {
    Serial.print("Switch ");
    Serial.print(i);
    Serial.print(": ");
    Serial.println((switchState & (1 << i)) ? "OFF" : "ON");
  }
  Serial.println();
  delay(500);

    // ads.setGain(GAIN_TWOTHIRDS);          // +/- 6.144V range

    // if (!ads.begin()) 
    // {
    //     Serial.println("Failed to initialize ADS1115");
    //     while (1);
    // }
    // Serial.println("Good Init ADC");
    
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(EN, OUTPUT);
    digitalWrite(IN1, LOW); // nor gates
    digitalWrite(IN2, LOW); // nor gates

    // init timers with the callback functions
    timer1.begin(togglePins);
    adcTimer.begin(readADC);
    
    digitalWrite(EN, HIGH);
    timer1.trigger(halfPeriod * 1000);    // start main timer

    while(1){;;}
    return 0;
}
