#include "ADS1115.h" 
//#include "UART.h"
//#include <Adafruit_ADS1015.h>
#include <Adafruit_ADS1X15.h>
#include <Wire.h>

Adafruit_ADS1115 ads;

#define LOGIC1 9     
#define LOGIC2 8     

void setup() {
  Serial.begin(9600);

  Serial.print("Setup Begin");

  // Set pin modes
  pinMode(LOGIC1, OUTPUT);  // Set pin B0 as output
  pinMode(LOGIC2, OUTPUT);  // Set pin D7 as output

  // Initialize pins to LOW
  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, LOW);

  Serial.print("Setup Done. \n");
  ads.begin();
}

void loop() {
//    float val; 
//    float val2;
  
  // Switch to first polarity
  digitalWrite(LOGIC2, LOW);
  digitalWrite(LOGIC1, HIGH);
  delay(500);
  Serial.print("L1 High. \n");


  // Switch to second polarity
  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, HIGH);
  delay(400);
  Serial.print("L2 High. \n");


//  // Read ADC values
//   val2 = ads1115_readADC_Diff_A0_1(0x48, DATARATE_128SPS, FSR_6_144);
//   val = ads1115_readADC_Diff_A2_3(0x48, DATARATE_128SPS, FSR_6_144);
//  
//   if(!ads.readADC_Differential_0_1()){
//     Serial.print("Read func returned Flase");
//   }
//   int16_t adc_val = ads.readADC_Differential_0_1();
//   Serial.print("AIN");Serial.print(": "); Serial.println(adc_val);


  delay(63); // datarate, timings and delays could be revisited, system is set for 1 hz squarewave
}
