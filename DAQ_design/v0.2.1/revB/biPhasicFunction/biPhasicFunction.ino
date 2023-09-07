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
  ADS.setGain(0);

  Serial.println("setup done");
}

void loop() {
  
  // Switch to first polarity
  digitalWrite(LOGIC2, LOW);
  digitalWrite(LOGIC1, HIGH);
  Serial.println("L1 High. \n");
  delay(500);

  // Switch to second polarity
  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, HIGH);
  Serial.println("L2 High. \n");
  delay(400);
  
  int16_t val_drop = ADS.readADC_Differential_2_3();  
  int16_t val_sense = ADS.readADC_Differential_0_1();
  
  float r = bigR(val_drop, val_sense);
  float volts_drop = ADS.toVoltage(val_drop); 
  float volts_sense = ADS.toVoltage(val_sense); 


  Serial.print("\tvDROP: "); Serial.print(val_drop); Serial.print("\t"); Serial.println(volts_drop, 3);
  Serial.print("\tvSENSE: "); Serial.print(val_sense); Serial.print("\t"); Serial.println(volts_sense, 3);
  Serial.print("\tStructure Resistance: "); Serial.print(r); Serial.print(" ohms");

  Serial.println();

  delay(63);
}

int16_t bigR(int16_t drop, int16_t sense){

  float i_calculated = drop/15000;
  float R = sense/i_calculated;

  return R;
}
