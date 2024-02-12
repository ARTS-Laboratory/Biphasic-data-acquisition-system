#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#define LOGIC1 9
#define LOGIC2 8

Adafruit_ADS1115 ads; 

unsigned long start_time = 0;
int frequency = 1; // Defualt to 1Hz
int in_line = 100; // Default to 100ohms

void setup() {
  Serial.begin(115200);

  pinMode(LOGIC1, OUTPUT);
  pinMode(LOGIC2, OUTPUT);

  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, LOW);

  // The ADC input range (or gain) can be changed via the following
  // functions, but be careful never to exceed VDD +0.3V max, or to
  // exceed the upper and lower limits if you adjust the input range!
  // Setting these values incorrectly may destroy your ADC!
  //                                                                ADS1015  ADS1115
  //                                                                -------  -------
     ads.setGain(GAIN_TWOTHIRDS);  // 2/3x gain +/- 6.144V  1 bit = 3mV      0.1875mV (default)
  // ads.setGain(GAIN_ONE);        // 1x gain   +/- 4.096V  1 bit = 2mV      0.125mV
  // ads.setGain(GAIN_TWO);        // 2x gain   +/- 2.048V  1 bit = 1mV      0.0625mV
  // ads.setGain(GAIN_FOUR);       // 4x gain   +/- 1.024V  1 bit = 0.5mV    0.03125mV
  // ads.setGain(GAIN_EIGHT);      // 8x gain   +/- 0.512V  1 bit = 0.25mV   0.015625mV
  // ads.setGain(GAIN_SIXTEEN);    // 16x gain  +/- 0.256V  1 bit = 0.125mV  0.0078125mV

    if(!ads.begin()){
    Serial.println("Failed to initialize ADS1115");
    while(1);
  }
  Serial.println("Good Init");

  Serial.println("Enter frequency (1, 2, 5, 10, 20, 50, 100, 200, 400):");
  while (!Serial.available());

  frequency = Serial.parseInt(); // Read requested frequency from user input
  Serial.print("Frequency set to: ");
  Serial.println(frequency);

  Serial.println("Enter in-line resistor value: ");
  while (!Serial.available());

  in_line = Serial.parseInt(); 
  Serial.print("In-line resistance set to: ");
  Serial.println(in_line);

  // Serial.print("vDROP Value,vDROP Voltage,");
  // Serial.print("vSENSE Value,vSENSE Voltage,");
  // Serial.println("Structure Resistance (ohms)");
}

void loop() {
  
  int half_period = 500 / frequency; 
  float m_region_tick = 0.8;
  int16_t result;
  float multiplier = 0.1875F; // For 16 bit dac @ +/-6.144V gain
  unsigned long measure_time = 0;

  if(start_time == 0) { // Check if start time hasn't been initialized
    start_time = millis(); // Record the time when LOGIC1 goes high for the first time
  }

  // Switch to Discharge Region
  digitalWrite(LOGIC2, LOW);
  digitalWrite(LOGIC1, HIGH);
  // Serial.print("L1 High,");
  delay(half_period);

  // Switch to Measurement Region
  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, HIGH);
  // Serial.print("L2 High,");
  delay(half_period*m_region_tick);

  measure_time = millis();
  
  int16_t val_drop = ads.readADC_Differential_2_3();  
  int16_t val_sense = ads.readADC_Differential_0_1();
  
  float volts_drop = val_drop * multiplier;
  float volts_sense = val_sense * multiplier; 
  float r = bigR(volts_drop, volts_sense, in_line);

  unsigned long elapsed_time = millis() - start_time;
  unsigned long elapsed_measure_time = millis() - measure_time;
  Serial.print(elapsed_measure_time); Serial.print("\t");
  Serial.print(elapsed_time); Serial.print("\t");
  Serial.print(val_drop); Serial.print("\t"); Serial.print(volts_drop, 7);Serial.print("\t");
  Serial.print(val_sense); Serial.print("\t"); Serial.print(volts_sense, 7);Serial.print("\t");
  Serial.println(r,7); 

  delay(half_period*0.1);
}


float bigR(float drop, float sense, int in_l){

  float i_calculated = drop/in_l;
  float R = sense/i_calculated;

  return R;
}
