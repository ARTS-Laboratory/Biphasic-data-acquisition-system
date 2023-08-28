#include <Wire.h>
//#include <Adafruit_ADS1X15.h>
#include "ADS1X15.h"

#define LOGIC1 9
#define LOGIC2 8

//Adafruit_ADS1115 ads; 
ADS1115 ADS(0x48);


void setup() {
  Serial.begin(9600);

  Serial.println("setup begin");

  pinMode(LOGIC1, OUTPUT);
  pinMode(LOGIC2, OUTPUT);

  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, LOW);

  if(!ADS.begin()){
    Serial.println("Failed to initialize ADS1115");
    while(1);
  }

  Serial.println("setup done");
}

void loop() {
  ADS.setGain(0);
  
  // Switch to first polarity
  digitalWrite(LOGIC2, LOW);
  digitalWrite(LOGIC1, HIGH);
  delay(500);
  Serial.println("L1 High. \n");

  // Switch to second polarity
  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, HIGH);
  delay(400);
  Serial.println("L2 High. \n");

  int16_t val_0 = ADS.readADC(0);  
  int16_t val_1 = ADS.readADC(1);  
  int16_t val_2 = ADS.readADC(2);  
  int16_t val_3 = ADS.readADC(3);  

  float f = ADS.toVoltage(2);  // voltage factor

  Serial.print("\tAnalog0: "); Serial.print(val_0); Serial.print('\t'); Serial.println(val_0 * f, 3);
  Serial.print("\tAnalog1: "); Serial.print(val_1); Serial.print('\t'); Serial.println(val_1 * f, 3);
  Serial.print("\tAnalog2: "); Serial.print(val_2); Serial.print('\t'); Serial.println(val_2 * f, 3);
  Serial.print("\tAnalog3: "); Serial.print(val_3); Serial.print('\t'); Serial.println(val_3 * f, 3);
  Serial.println();
}
