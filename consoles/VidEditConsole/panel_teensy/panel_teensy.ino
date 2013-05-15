#include <SPI.h>
#include <stdint.h>
#include <avr/interrupt.h>

const int DATA_IN = 18;
const int SH_OUT = 17;
const int ST_OUT = 16;
const int PL_OUT = 15;

const int L_COUNT = 3*16;

enum LEDState {
  L_OFF =0,
  L_ON =1,
  L_FLASH_A =2,
  L_FLASH_B =3,
  L_FLICKER =4,

  L_LAST
};

const uint8_t ILLUMINATED_COUNT = 25;
const uint8_t illuminated_mapping[ILLUMINATED_COUNT] = {
  31, 30, 29, 28, 27, 26, 25, 24,
  23, 21, 19, 17, 15, 22, 20, 18,
  16, 14, 13, 12, 11, 10, 9,  8,
  7 };
const uint8_t LED_COUNT = 12;
const uint8_t led_mapping[LED_COUNT] = {
  36, 38, 39, 40, 43, 45, 46, 47,
  41, 42, 44, 37 };

class LEDMap {
private:  
  uint8_t l[L_COUNT];
public:
  void clear();
  void setRaw(int idx, LEDState value);
  void setLED(int idx, LEDState value);
  void setIlluminated(int idx, LEDState value);
  void show(int cycle);
};

void LEDMap::clear() {
  for (int i = 0; i < L_COUNT; i++) l[i] = L_OFF;
}

void LEDMap::setRaw(int idx, LEDState value) {
  l[idx] = value;
}

void LEDMap::setLED(int idx, LEDState value) {
  l[led_mapping[idx]] = value;
}

void LEDMap::setIlluminated(int idx, LEDState value) {
  l[illuminated_mapping[idx]] = value;
}

void LEDMap::show(int cycle) {
  for (int8_t i = 0; i < L_COUNT; ) {
    uint8_t b = 0;
    for (int8_t j = 0; j < 8; j++, i++) {
      b <<= 1;
      if (i < L_COUNT) {
        const uint8_t s = l[i];
        if (s == L_ON) b |= 0x01;
        else if (s == L_FLASH_A && cycle < 128) b |= 0x01;
        else if (s == L_FLASH_B && cycle >= 128) b |= 0x01;
        else if (s == L_FLICKER && (cycle % 32) < 17) b |= 0x01;
        // handle other modes
      }
    }
    SPI.transfer(b);
  }   
}

LEDMap l;

void setup() {
  l.clear();
  // initialize SPI:
  SPI.begin(); 
  SPI.setClockDivider(SPI_CLOCK_DIV16);
  pinMode(DATA_IN, INPUT);
  pinMode(SH_OUT, OUTPUT);
  pinMode(ST_OUT, OUTPUT);
  pinMode(PL_OUT, OUTPUT);
  digitalWrite(PL_OUT,LOW);
  digitalWrite(ST_OUT,LOW);
  digitalWrite(SH_OUT,LOW);
  Serial.begin(9600);
  Serial.println("Ready.");
  // Init timer3: Fast PWM mode, 10-bit (0111)
  TCCR3A = 0x03;
  TCCR3B = 0x08 | 0x03; // cs = 3; 1/64 prescaler
  TCCR3C = 0x00;
  TIMSK3 = 0x01; // enable overflow interrupt
}


void readKeys() {
  digitalWrite(PL_OUT,HIGH);
    delayMicroseconds(5);
  digitalWrite(ST_OUT,HIGH);
    delayMicroseconds(5);
  digitalWrite(ST_OUT,LOW);
    delayMicroseconds(5);
  digitalWrite(PL_OUT,LOW);
    delayMicroseconds(5);
  digitalWrite(ST_OUT,HIGH);
    delayMicroseconds(5);
  digitalWrite(ST_OUT,LOW);
    delayMicroseconds(5);
  digitalWrite(PL_OUT,HIGH);
    delayMicroseconds(5);
  for (int i = 0; i < 16; i++) {
    digitalWrite(SH_OUT,HIGH);
    Serial.print(digitalRead(DATA_IN));
    digitalWrite(SH_OUT,LOW);
    delayMicroseconds(5);
  }
  Serial.println();
  digitalWrite(PL_OUT,LOW);
}

void exec(char *buf) {
  char cmd = buf[0];
  switch(cmd) {
    case 'r':
      readKeys();
      break;
    case 'l':
      l.setLED(buf[1],(LEDState)buf[2]);
      break;
    case 'i':
      l.setIlluminated(buf[1],(LEDState)buf[2]);
  }
}
  
int i = 0;
char buf[20];
int bidx = 0;

void loop() {
  int r;
  while ((r=Serial.read()) != -1) {
    if (r == '\n' || r == '\r') {
      buf[bidx] = 0;
      exec(buf);
      bidx = 0;
    } else {
      buf[bidx++] = r;
      if (bidx > 19) bidx = 19;
    }
  }
}

volatile uint8_t cycle = 0;
ISR(TIMER3_OVF_vect) {
  l.show(cycle++);
}
