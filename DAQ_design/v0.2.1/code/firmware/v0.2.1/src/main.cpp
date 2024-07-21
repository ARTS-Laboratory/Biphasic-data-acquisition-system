#include "Arduino.h"
#include "TeensyTimerTool.h"
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_ADS1X15.h>
#include <SD.h>

using namespace TeensyTimerTool;
Adafruit_ADS1115 ads;
OneShotTimer timer1;
OneShotTimer adcTimer;

const int in1 = 0;
const int in2 = 1;
int frequency = 10;                       // in Hz
bool toggleState = false;
int period = 1000 / frequency;            // period in milliseconds
int halfPeriod = period / 2;              // half period for 50% duty cycle
int adcDelay = halfPeriod * 0.8;          // 80% of half period
float in_line = 100000;                   // value of known resistor
const float multiplier = 0.1875F;         // for 16 bit dac @ +/-6.144V gain
const int chipSelect = 10;
char buffer[64]; 
char resistance_str[16];
File dataFile;

void togglePins()
{
    if (toggleState)
    {
        digitalWriteFast(in1, HIGH);
        digitalWriteFast(in2, LOW);
        adcTimer.trigger(adcDelay * 1000); // convert to microseconds
    }
    else
    {
        digitalWriteFast(in1, LOW);
        digitalWriteFast(in2, HIGH);
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
    int16_t val_drop = ads.readADC_Differential_2_3();  
    int16_t val_sense = ads.readADC_Differential_0_1();

    float r = bigR(val_drop, val_sense, in_line);

    dtostrf(r, 6, 3, resistance_str);
    snprintf(buffer, sizeof(buffer), "%s", resistance_str);

    dataFile = SD.open("data.txt", FILE_WRITE);
    if (dataFile) {
        dataFile.println(buffer);
        dataFile.close();
    } else {
        Serial.println("error opening data.txt");
    }
}

int main() 
{
    Serial.begin(115200);

    Serial.print("Initializing SD card...");

    if (!SD.begin(chipSelect)) {
      Serial.println("initialization failed. Things to check:");
      Serial.println("1. is a card inserted?");
      Serial.println("2. is your wiring correct?");
      Serial.println("3. did you change the chipSelect pin to match your shield or module?");
      Serial.println("Note: press reset button on the board and reopen this Serial Monitor after fixing your issue!");
      while (true);
    }

    Serial.println("initialization done.");

    ads.setGain(GAIN_TWOTHIRDS);          // +/- 6.144V range

    if (!ads.begin()) 
    {
        Serial.println("Failed to initialize ADS1115");
        while (1);
    }
    Serial.println("Good Init ADC");
    
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);

    // init timers with the callback functions
    timer1.begin(togglePins);
    adcTimer.begin(readADC);
    
    timer1.trigger(halfPeriod * 1000);    // start main timer

    while(1){;;}
    return 0;
}
