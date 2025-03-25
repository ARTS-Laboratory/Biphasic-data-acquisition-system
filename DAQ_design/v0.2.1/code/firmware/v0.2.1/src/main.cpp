#include "parameters.h"

using namespace TeensyTimerTool;
Adafruit_ADS1115 ads;
OneShotTimer timer1;
OneShotTimer adcTimer;

int frequency = 10;                       /* in Hz */
bool toggleState = false;
int period = 1000 / frequency;            /* period in milliseconds */
int halfPeriod = period / 2;              /* half period for 50% duty cycle */
int adcDelay = halfPeriod * 0.8;          /* 80% of half period */
float in_line = 180000;                   /* value of known resistor */
const float multiplier = 0.1875F;         /* for 16 bit dac @ +/-6.144V gain */
char buffer[64]; 
char resistance_str[16];
uint8_t switchState;

int16_t val_drop; 
int16_t val_sense;
float r;
char r_str[10];
char s_str[10];
char d_str[10];

void readDIPSwitches(uint8_t& switchState) {
  digitalWrite(LATCH_PIN, LOW);  /* Pulse the latch pin to load the parallel data */
  delayMicroseconds(5);
  digitalWrite(LATCH_PIN, HIGH);
  
  for (int i = 0; i < 8; i++) {
    switchState |= (digitalRead(DATA_PIN) << i); /* Read each bit */
    digitalWrite(CLOCK_PIN, HIGH); /* Pulse the clock to shift the next bit */
    delayMicroseconds(5);
    digitalWrite(CLOCK_PIN, LOW);
  }
  switchState = ~switchState;
}

void togglePins()
{
    if (toggleState)
    {
			  CORE_PIN14_PORTSET = CORE_PIN14_BITMASK;
			  CORE_PIN15_PORTCLEAR = CORE_PIN15_BITMASK;
        adcTimer.trigger(adcDelay * 1000); /* convert to microseconds */
    }
    else
    {
			  CORE_PIN14_PORTCLEAR = CORE_PIN14_BITMASK;
			  CORE_PIN15_PORTSET = CORE_PIN15_BITMASK;
    }
    toggleState = !toggleState;

    timer1.trigger(halfPeriod * 1000);    /* restart the main timer for the next toggle */
}

void readADC() 
{
  digitalWrite(LEDACT, HIGH);
  val_sense = ads.readADC_Differential_0_1();  
  val_drop = ads.readADC_Differential_2_3();

  r = bigR(val_drop, val_sense, in_line);
  
  dtostrf(r, 6, 3, r_str);
  dtostrf(val_sense, 6, 3, s_str);
  dtostrf(val_drop, 6, 3, d_str);
  
  snprintf(buffer, sizeof(buffer), "%s,%s,%s", r_str, s_str, d_str);
  File dataFile = SD.open("data.txt", FILE_WRITE);
  if (dataFile) {
    dataFile.println(buffer);
    dataFile.close();
    digitalWrite(LEDACT, LOW);
  } else {
    Serial.println("Error opening data.txt");
  }
}

int main() 
{
  Serial.begin(9600);
  
  pinMode(LEDPOW, OUTPUT);
  digitalWrite(LEDPOW, HIGH);
  pinMode(LEDACT, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(EN, OUTPUT);
  digitalWrite(IN1, LOW); /* nor gates */
  digitalWrite(IN2, LOW); /* nor gates */
  digitalWrite(EN, HIGH);
  pinMode(LATCH_PIN, OUTPUT);
  pinMode(CLOCK_PIN, OUTPUT);
  pinMode(DATA_PIN, INPUT);

  ads.setGain(GAIN_ONE);          /* +/- 4.096V range */

  if (!ads.begin()) 
  {
      Serial.println("Failed to initialize ADS1115");
      while (1);
  }
  Serial.println("Good Init ADC");

  if (!SD.begin(SD_CS)) {
      Serial.println("SD card initialization failed!");
      while (1);
  }
  Serial.println("SD card initialized.");
  
  readDIPSwitches(switchState);
  Serial.print("Raw switchState: ");
  Serial.println(switchState);

  /* callbacks to init timers */
  timer1.begin(togglePins);
  adcTimer.begin(readADC);
  
  digitalWrite(EN, LOW);
  timer1.trigger(halfPeriod * 1000);    /* start main timer */

  while(1){;;}
  return 0;
}
