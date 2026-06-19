#include <Arduino.h>

#define LOGIC1 9 
#define LOGIC2 8
#define SYNC_PIN 4 // optional marker to NI side

unsigned long start_time = 0;
float userfrq = 1;
float period = 1;

// ISR Flag
volatile bool toggle_flag = false;

// Logic flag
bool L_state = false;
bool readchk = false;
unsigned long high_state_start_time = 0;
unsigned long high_state_duration = 0;

void setup(){
  Serial.begin(115200);

  pinMode(LOGIC1, OUTPUT);
  pinMode(LOGIC2, OUTPUT);
  pinMode(SYNC_PIN, OUTPUT);

  digitalWrite(LOGIC1, LOW);
  digitalWrite(LOGIC2, LOW);
  digitalWrite(SYNC_PIN, LOW);

  //Serial.println("Enter frequency in Hz (1, 2, 5, 10, 20, 50, 100):");
  //while (!Serial.available());

//  userfrq = Serial.parseFloat(); // Read requested period from user input
//  Serial.print("frequency set to: ");
//  Serial.println(userfrq);

float userfrq = 1.0; // presetting freq so i dont have to plug in usb

unsigned long start = millis();

while (!Serial.available() && millis() - start < 3000) {
}

if (Serial.available()) {
    userfrq = Serial.parseFloat();
}

  // half-period in ms for each h-bridge state
  high_state_duration = (unsigned long)(500000.0 / userfrq);

  // Serial.println("Enter in-line resistor value: ");
  // while (!Serial.available());

  // in_line = Serial.parseInt(); 
  // Serial.print("In-line resistance set to: ");
  // Serial.println(in_line);

  // Init timer1
  noInterrupts();   // disables global interrupts
  TCCR1A = 0;       // sets entire TCCR1A register to 0
  TCCR1B = 0;       // same for TCCR1B

  // Calculate OCR1A value
  float clockSpeed = 16000000.0; // Arduino clock speed in Hz
  float prescaler = 1024.0; // Prescaler value
  float tempOCR1A = clockSpeed / (prescaler * (2*userfrq)) - 1;

  unsigned long user_fq = static_cast<unsigned long>(round(tempOCR1A));

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

//#ifdef DEBUG
//  unsigned long calculated_period = clockSpeed / (prescaler * (OCR1A + 1));
//  Serial.print("Calculated period: ");
//  Serial.print(calculated_period);
//  Serial.println(" Hz");
//  Serial.print("user_fq: ");
//  Serial.println(user_fq);
//  Serial.print("OCR1A Value: ");
//  Serial.println(OCR1A);
//#endif
}

void loop() {
  if (toggle_flag) {
    toggleHbridge();
    toggle_flag = false;
  }

  if (!readchk && L_state &&
      (micros() - high_state_start_time >= (unsigned long)(0.8 * high_state_duration))) {

    // optional sync pulse for NI acquisition
    digitalWrite(SYNC_PIN, HIGH);
    delayMicroseconds(20);
    digitalWrite(SYNC_PIN, LOW);

    readchk = true;
  }
}

// Timer1 ISR
ISR(TIMER1_COMPA_vect) {
  toggle_flag = true;
}

void toggleHbridge() {
  L_state = !L_state;

  if(L_state){
    readchk = false;
    digitalWrite(LOGIC1, HIGH);
    digitalWrite(LOGIC2, LOW);
    high_state_start_time = micros(); // Start timing the high state
  } else {
    digitalWrite(LOGIC1, LOW);
    digitalWrite(LOGIC2, HIGH);
  }
}

//float bigR(float drop, float sense, int in_l){

//  float i_calculated = drop/in_l;
//  float R = sense/i_calculated;

//  return R;
//}