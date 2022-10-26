#define F_CPU 16000000UL
#include <avr/io.h> // This contains the definitions of the terms used
#include <util/delay.h> // This contains the definition of delay function
#include <ADS1115.h>
#include <avr/interrupt.h> // This contains the definitions of the terms used
#include <UART.h>


int16_t val;
int16_t val2;

int i = 0;
void main()
{
//UART INITIALIZATION
UART_init(8);

DDRB = 0b00000001; // Port B0 (Pin 4 in the ATmega) made output 
DDRD = 0b10000000; // Port D7 (Pin 4 in the ATmega) made output 

PORTD = 0b00000000; // PINd7 LOW
PORTB = 0b00000000; // PINb0 LOW

// !!never set both b0 and d7 high!! causes a short circuit in H-bridge

TWSR=0x00; //set presca1er bits to zero
TWBR=0x48; //SCL frequency for 16Mhz
TWCR=0x04; //enab1e TWI module	


while(1)
{
PORTD = 0b00000000; // PINd7 LOW
PORTB = 0b00000001; // PINb0 HIGH

//PORTB = 0b00000000; // PIN LOW
//PORTD = 0b10000000; // PIN HIGH

_delay_ms(500); //

PORTB = 0b00000000; // PINb0 LOW
PORTD = 0b10000000; // PINd7 HIGH

_delay_ms(400); // 

val2 = ads1115_readADC_Diff_A0_1(0x48,DATARATE_128SPS, FSR_6_144);
val = ads1115_readADC_Diff_A2_3(0x48,DATARATE_128SPS, FSR_6_144);

UART_putS16_2ch(val2,val);
_delay_ms(63); // datarate, timings and delays could be revisited, system is set for 1 hz squarewave // see ads1115.h
}

}

