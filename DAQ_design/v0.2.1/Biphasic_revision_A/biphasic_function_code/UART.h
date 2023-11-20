#ifndef UART
#define UART

#include <avr/io.h>
void UART_init(uint16_t ubrr);
void UART_putc(unsigned char data);
void UART_puts(char* s);
void UART_puthex8(uint8_t val);
void UART_puthex16(uint16_t val);
void UART_putU8(uint8_t val);
void UART_putS8(int8_t val);
void UART_putU16(uint16_t val);
void UART_putS16(int16_t val);
void UART_putS16_2ch(int16_t val,int16_t val2);


void UART_init(uint16_t ubrr)
{
    // set baudrate in UBRR
    UBRR0L = (uint8_t)(ubrr & 0xFF);
    UBRR0H = (uint8_t)(ubrr >> 8);
	UCSR0C = 0x06;
    // enable the transmitter and receiver
    UCSR0B |= (1 << RXEN0) | (1 << TXEN0);
}
void UART_putc(unsigned char data)
{
    // wait for transmit buffer to be empty
    while(!(UCSR0A & (1 << UDRE0)));

    // load data into transmit register
    UDR0 = data;
}
void UART_puts(char* s)
{
    // transmit character until NULL is reached
    while(*s > 0) UART_putc(*s++);
}
void UART_puthex8(uint8_t val)
{
    // extract upper and lower nibbles from input value
    uint8_t upperNibble = (val & 0xF0) >> 4;
    uint8_t lowerNibble = val & 0x0F;

    // convert nibble to its ASCII hex equivalent
    upperNibble += upperNibble > 9 ? 'A' - 10 : '0';
    lowerNibble += lowerNibble > 9 ? 'A' - 10 : '0';

    // print the characters
    UART_putc(upperNibble);
    UART_putc(lowerNibble);
}
void UART_puthex16(uint16_t val)
{
    // transmit upper 8 bits
    UART_puthex8((uint8_t)(val >> 8));

    // transmit lower 8 bits
    UART_puthex8((uint8_t)(val & 0x00FF));
}
void UART_putU8(uint8_t val)
{
    uint8_t dig1 = '0', dig2 = '0';

    // count value in 100s place
    while(val >= 100)
    {
        val -= 100;
        dig1++;
    }

    // count value in 10s place
    while(val >= 10)
    {
        val -= 10;
        dig2++;
    }

    // print first digit (or ignore leading zeros)
    if(dig1 != '0') UART_putc(dig1);

    // print second digit (or ignore leading zeros)
    if((dig1 != '0') || (dig2 != '0')) UART_putc(dig2);

    // print final digit
    UART_putc(val + '0');
}
void UART_putS8(int8_t val)
{
    // check for negative number
    if(val & 0x80)
    {
        // print negative sign
        UART_putc('-');

        // get unsigned magnitude
        val = ~(val - 1);
    }

    // print magnitude
    UART_putU8((uint8_t)val);
}
void UART_putU16(uint16_t val)
{
    uint8_t dig1 = '0', dig2 = '0', dig3 = '0', dig4 = '0';

    // count value in 10000s place
    while(val >= 10000)
    {
        val -= 10000;
        dig1++;
    }

    // count value in 1000s place
    while(val >= 1000)
    {
        val -= 1000;
        dig2++;
    }

    // count value in 100s place
    while(val >= 100)
    {
        val -= 100;
        dig3++;
    }

    // count value in 10s place
    while(val >= 10)
    {
        val -= 10;
        dig4++;
    }

    // was previous value printed?
    uint8_t prevPrinted = 0;

    // print first digit (or ignore leading zeros)
    if(dig1 != '0') {UART_putc(dig1); prevPrinted = 1;}

    // print second digit (or ignore leading zeros)
    if(prevPrinted || (dig2 != '0')) {UART_putc(dig2); prevPrinted = 1;}

    // print third digit (or ignore leading zeros)
    if(prevPrinted || (dig3 != '0')) {UART_putc(dig3); prevPrinted = 1;}

    // print third digit (or ignore leading zeros)
    if(prevPrinted || (dig4 != '0')) {UART_putc(dig4); prevPrinted = 1;}

    // print final digit
    UART_putc(val + '0');
}
void UART_putS16(int16_t val)
{
    // check for negative number
    if(val & 0x8000)
    {
        // print minus sign
        UART_putc('-');

        // convert to unsigned magnitude
        val = ~(val - 1);
    }

    // print unsigned magnitude
    UART_putU16((uint16_t) val);
	UART_putc('\n');

}
void UART_putS16_2ch(int16_t val,int16_t val2)
{
    // check for negative number
    if(val & 0x8000)
    {
        // print minus sign
        UART_putc('-');

        // convert to unsigned magnitude
        val = ~(val - 1);
    }
	    // check for negative number


    // print unsigned magnitude
    UART_putU16((uint16_t) val);
	UART_putc(' ');
	
    if(val2 & 0x8000)
    {
        // print minus sign
        UART_putc('-');

        // convert to unsigned magnitude
        val2 = ~(val2 - 1);
    }
    UART_putU16((uint16_t) val2);

	UART_putc('\n');

}
#endif
