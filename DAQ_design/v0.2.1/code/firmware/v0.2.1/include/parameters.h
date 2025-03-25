#include "Arduino.h"
#include "TeensyTimerTool.h"
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_ADS1X15.h>

#define IN1 14
#define IN2 15
#define EN 2
#define LEDPOW 3
#define LEDACT 4
#define DATA_PIN 23
#define LATCH_PIN 18
#define CLOCK_PIN 19


float bigR(float drop, float sense, float in_l)
{
    // float i_calculated = (drop * multiplier) / in_l;
    float i_calculated = (drop * 0.1875f) / in_l;
    float R = (sense * 0.1875f) / i_calculated;
    return R;
}

