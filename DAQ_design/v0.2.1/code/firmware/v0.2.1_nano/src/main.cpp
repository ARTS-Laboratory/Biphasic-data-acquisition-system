#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <Adafruit_ADS1X15.h>

#define LOGIC1 9 
#define LOGIC2 8
//#define DEBUG

Adafruit_ADS1115 ads;

unsigned long start_time = 0;
float userfrq = 10.0f;
float period = 1.0f;
float in_line = 10000.0f;
const float multiplier = 0.1875F;         // For 16 bit dac @ +/-6.144V gain
volatile bool toggle_flag = false;        // ISR flag
bool L_state = false;                     // Logic flag
bool readchk = false;
unsigned long high_state_start_time = 0;
unsigned long high_state_duration = 0;
char buffer[64]; 
char resistance_str[16];
int signalType = 0;                       // 0 for biphasic, 1 for pure DC

int16_t val_drop; 
int16_t adc2;
int16_t adc3;
float sense1;
float sense2;
float r1;
float r2;
char r1_str[10];
char r2_str[10];
char s1_str[10];
char s2_str[10];


void toggleHbridge()
{
  if (signalType == 1) 
  {
    // Pure DC mode, keep LOGIC1 high
    L_state = true;
    readchk = false;
    digitalWrite(LOGIC1, HIGH);
    digitalWrite(LOGIC2, LOW);
  } 
  else 
  {
    // Biphasic mode
    L_state = !L_state;
    if (L_state) 
    {
      readchk = false;
      digitalWrite(LOGIC1, HIGH);
      digitalWrite(LOGIC2, LOW);
      high_state_start_time = micros(); // Start timing the high state
    } 
    else 
    {
      digitalWrite(LOGIC1, LOW);
      digitalWrite(LOGIC2, HIGH);
    }
  }
}

float bigR(float drop, float sense, float in_l)
{
  float i_calculated = (drop * multiplier) / in_l;
  float R = sense / i_calculated;
  return R;
}

void readADC() 
{
  if (start_time == 0) {   // Check if start time hasn't been initialized
    start_time = millis(); // Record the time when LOGIC1 goes high for the first time
  }

  val_drop = ads.readADC_Differential_0_1();  
  
  adc2 = ads.readADC_SingleEnded(2);
  adc3 = ads.readADC_SingleEnded(3);
  sense1 = ads.computeVolts(adc2);
  sense2 = ads.computeVolts(adc3);

  r1 = bigR(val_drop, sense1, in_line);
  r2 = bigR(val_drop, sense2, in_line);
  
  unsigned long elapsed_time = millis() - start_time;
  
  dtostrf(r1, 6, 3, r1_str);
  dtostrf(r2, 6, 3, r2_str);
  dtostrf(sense1, 6, 3, s1_str);
  dtostrf(sense2, 6, 3, s2_str);
  
  snprintf(buffer, sizeof(buffer), "%lu,%s,%s,%s,%s", elapsed_time, r1_str, r2_str, s1_str, s2_str);
  Serial.println(buffer);
}


void setup() 
{
  Serial.begin(9600);
  pinMode(LOGIC1, OUTPUT);
  pinMode(LOGIC2, OUTPUT);

  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, LOW);

  ads.setGain(GAIN_TWOTHIRDS); // +/- 6.144V range

  if (!ads.begin()) 
  {
    Serial.println("Failed to initialize ADS1115");
    while (1);
  }
  Serial.println("Good Init");

  // Serial.println("Enter signal type (0 for biphasic, 1 for pure DC):");
  // while (!Serial.available());

  // signalType = Serial.parseInt();
  // Serial.print("Signal type set to: ");
  // Serial.println(signalType == 0 ? "Biphasic" : "Pure DC");

  // Serial.println("Enter frequency in Hz (1, 2, 5, 10, 20):");
  // while (!Serial.available());

  // userfrq = Serial.parseFloat();
  // Serial.print("Frequency set to: ");
  // Serial.println(userfrq);
  userfrq = (2 * userfrq);
  period = (1.0 / userfrq);

  // Init timer1
  noInterrupts();   // disables global interrupts
  TCCR1A = 0;       // sets entire TCCR1A register to 0
  TCCR1B = 0;       // same for TCCR1B

  // Calculate OCR1A value
  float clockSpeed = 16000000.0; // Arduino clock speed in Hz
  float prescaler = 1024.0; // Prescaler value
  float tempOCR1A = clockSpeed / (prescaler * userfrq) - 1;

  unsigned long user_fq = static_cast<unsigned long>(round(tempOCR1A));

  if (user_fq < 1) 
  {
    user_fq = 1; // Minimum practical value to avoid too fast interrupts
  } else if (user_fq > 65535) 
  {
    user_fq = 65535; // Maximum value for a 16-bit timer
  }

  OCR1A = user_fq;    // 15624 = 16MHz / (1024 * 1Hz) - 1

  // Enables CTC mode
  TCCR1B |= (1 << WGM12);

  // Sets CS10 and CS12 bits for 1024 prescaler
  TCCR1B |= (1 << CS10);
  TCCR1B |= (1 << CS12);

  // Enables timer compare IRQ
  TIMSK1 |= (1 << OCIE1A);

  interrupts();
  high_state_duration = period * 1E6; // High state duration in microseconds

#ifdef DEBUG
  unsigned long calculated_period = clockSpeed / (prescaler * (OCR1A + 1));
  Serial.print("Calculated period: ");
  Serial.print(calculated_period);
  Serial.println(" Hz");
  Serial.print("User_fq: ");
  Serial.println(user_fq);
  Serial.print("OCR1A Value: ");
  Serial.println(OCR1A);
#endif
}

void loop() 
{
  if (toggle_flag) 
  {
    toggleHbridge();
    toggle_flag = false;
  }

  // Check if H-bridge is high and ~80% through its duty cycle
  if (!readchk && L_state && (micros() - high_state_start_time >= 0.75 * high_state_duration)) 
  {
    readADC();
    readchk = true;
  }
}

// Timer1 ISR
ISR(TIMER1_COMPA_vect) 
{
  toggle_flag = true;
}
