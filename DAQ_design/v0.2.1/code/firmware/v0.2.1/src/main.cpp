#include "Arduino.h"
#include "TeensyTimerTool.h"
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_ADS1X15.h>

using namespace TeensyTimerTool;
Adafruit_ADS1115 ads;
OneShotTimer timer1;
OneShotTimer adcTimer;

const int in1 = 0;
const int in2 = 1;
const int en = 2;
int frequency = 500;                       // in Hz
bool toggleState = false;
int period = 1000 / frequency;            // period in milliseconds
int halfPeriod = period / 2;              // half period for 50% duty cycle
int adcDelay = halfPeriod * 0.8;          // 80% of half period
float in_line = 680000;                   // value of known resistor
const float multiplier = 0.1875F;         // for 16 bit dac @ +/-6.144V gain
char buffer[64]; 
char resistance_str[16];

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



float bigR(float drop, float sense, float in_l)
{
    float i_calculated = (drop * multiplier) / in_l;
    float R = (sense * multiplier) / i_calculated;
    return R;
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
    Serial.begin(115200);

    // ads.setGain(GAIN_TWOTHIRDS);          // +/- 6.144V range

    // if (!ads.begin()) 
    // {
    //     Serial.println("Failed to initialize ADS1115");
    //     while (1);
    // }
    // Serial.println("Good Init ADC");
    
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    pinMode(en, OUTPUT);
    digitalWrite(in1, LOW); // nor gates
    digitalWrite(in2, LOW); // nor gates

    // init timers with the callback functions
    timer1.begin(togglePins);
    adcTimer.begin(readADC);
    
    digitalWrite(en, HIGH);
    timer1.trigger(halfPeriod * 1000);    // start main timer

    while(1){;;}
    return 0;
}
