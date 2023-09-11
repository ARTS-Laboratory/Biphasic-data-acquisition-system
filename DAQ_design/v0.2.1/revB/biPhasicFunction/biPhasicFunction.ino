#include <Wire.h>
#include "ADS1X15.h"

#define LOGIC1 9
#define LOGIC2 8

//Adafruit_ADS1115 ads; 
ADS1115 ADS(0x48);

unsigned long startTime = 0;

void setup() {
  Serial.begin(9600);

  // Serial.println("setup begin");

  pinMode(LOGIC1, OUTPUT);
  pinMode(LOGIC2, OUTPUT);

  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, LOW);

  if(!ADS.begin()){
    Serial.println("Failed to initialize ADS1115");
    while(1);
  }
  ADS.setGain(0);

  // Serial.println("setup done");

  // Serial.print("vDROP Value,vDROP Voltage,");
  // Serial.print("vSENSE Value,vSENSE Voltage,");
  // Serial.println("Structure Resistance (ohms)");
}

void loop() {
  
  if(startTime == 0) { // Check if start time hasn't been initialized
    startTime = millis(); // Record the time when LOGIC1 goes high for the first time
  }

  // Switch to first polarity
  digitalWrite(LOGIC2, LOW);
  digitalWrite(LOGIC1, HIGH);
  // Serial.print("L1 High,");
  delay(500);

  // Switch to second polarity
  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, HIGH);
  // Serial.print("L2 High,");
  delay(400);
  
  int16_t val_drop = ADS.readADC_Differential_2_3();  
  int16_t val_sense = ADS.readADC_Differential_0_1();
  
  float volts_drop = ADS.toVoltage(val_drop); 
  float volts_sense = ADS.toVoltage(val_sense); 
  float r = bigR(volts_drop, volts_sense);

  unsigned long elapsedTime = millis() - startTime;
  Serial.print(elapsedTime); Serial.print("\t");
  Serial.print(val_drop); Serial.print("\t"); Serial.print(volts_drop, 7);Serial.print("\t");
  Serial.print(val_sense); Serial.print("\t"); Serial.print(volts_sense, 7);Serial.print("\t");
  Serial.println(r,7); 

  delay(63);
}


float bigR(float drop, float sense){

  float i_calculated = drop/15000;
  float R = sense/i_calculated;

  return R;
}
