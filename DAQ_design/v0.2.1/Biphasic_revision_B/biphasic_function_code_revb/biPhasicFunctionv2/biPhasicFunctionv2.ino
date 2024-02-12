#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

#define LOGIC1 9 
#define LOGIC2 8
//#define DEBUG

Adafruit_ADS1115 ads;

unsigned long start_time = 0;
float frequency = 1;
int in_line = 100;
const float multiplier = 0.1875F; // For 16 bit dac @ +/-6.144V gain

// ISR Flag
volatile bool toggle_flag = false;

// Logic flag
bool L_state = false;
unsigned long high_state_start_time = 0;
unsigned long high_state_duration = 0;

void setup(){
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

  frequency = Serial.parseFloat(); // Read requested frequency from user input
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

  // Init timer1
  noInterrupts();   // disables global interrupts
  TCCR1A = 0;       // sets entire TCCR1A register to 0
  TCCR1B = 0;       // same for TCCR1B

  // Calculate OCR1A value
  float clockSpeed = 16000000.0; // Arduino clock speed in Hz
  float prescaler = 1024.0; // Prescaler value
  float tempOCR1A = clockSpeed / (prescaler * frequency) - 1;

  // Round and convert to unsigned long
  unsigned long user_fq = static_cast<unsigned long>(round(tempOCR1A));

  // Validation
  if (user_fq < 1) {
      user_fq = 1; // Minimum practical value to avoid too fast interrupts
  } else if (user_fq > 65535) {
      user_fq = 65535; // Maximum value for a 16-bit timer
  }
  OCR1A = user_fq;    // 15624 = 16MHz / (1024 * 1Hz) - 1

  // Turns on CTC mode
  TCCR1B |= (1 << WGM12);

  // Sets CS10 and CS12 bits for 1024 prescaler
  TCCR1B |= (1 << CS10);
  TCCR1B |= (1 << CS12);

  // Enables timer compare IRQ
  TIMSK1 |= (1 << OCIE1A);

  interrupts();
  high_state_duration = 500 / frequency; // in milliseconds

#ifdef DEBUG
  unsigned long calculated_frequency = clockSpeed / (prescaler * (OCR1A + 1));
  Serial.print("Calculated Frequency: ");
  Serial.print(calculated_frequency);
  Serial.println(" Hz");
  Serial.print("user_fq: ");
  Serial.println(user_fq);
  Serial.print("OCR1A Value: ");
  Serial.println(OCR1A);
#endif
}

void loop() {
  if (toggle_flag) {
    toggleHbridge();
    toggle_flag = false;
  }

  // Check if H-bridge is high and 80% through its duty cycle
  while(!(L_state && (micros() - high_state_start_time = 0.8 * high_state_duration))); 
  readADC();
}

// Timer1 ISR
ISR(TIMER1_COMPA_vect) {
  toggle_flag = true;
}

void toggleHbridge() {
  L_state = !L_state;

  if(L_state){
    Serial.println("H-bridge high");
    digitalWrite(LOGIC1, HIGH);
    digitalWrite(LOGIC2, LOW);
    high_state_start_time = micros(); // Start timing the high state
  } else {
    Serial.println("H-bridge low");
    digitalWrite(LOGIC1, LOW);
    digitalWrite(LOGIC2, HIGH);
  }
}

void readADC() {
  // if(start_time == 0) { // Check if start time hasn't been initialized
  //   start_time = millis(); // Record the time when LOGIC1 goes high for the first time
  // }

  // int16_t val_drop = ads.readADC_Differential_2_3();  
  // int16_t val_sense = ads.readADC_Differential_0_1();
  
  // float volts_drop = val_drop * multiplier;
  // float volts_sense = val_sense * multiplier; 
  // float r = bigR(volts_drop, volts_sense, in_line);
  // unsigned long elapsed_time = millis() - start_time;

  // Serial.print(elapsed_time); Serial.print("\t");
  // Serial.print(val_drop); Serial.print("\t"); Serial.print(volts_drop, 7);Serial.print("\t");
  // Serial.print(val_sense); Serial.print("\t"); Serial.print(volts_sense, 7);Serial.print("\t");
  // Serial.println(r,7); 
}

float bigR(float drop, float sense, int in_l){

  float i_calculated = drop/in_l;
  float R = sense/i_calculated;

  return R;
}