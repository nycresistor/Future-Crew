#include <SPI.h>
#include <stdint.h>
#include <avr/interrupt.h>

const int L_COUNT = 3*16;

const int LATCH_PIN = 18;
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
  digitalWrite(LATCH_PIN,LOW);
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
  digitalWrite(LATCH_PIN,HIGH);
}

LEDMap l;

void setup() {
  l.clear();
  pinMode(LATCH_PIN,OUTPUT);
  digitalWrite(LATCH_PIN,HIGH);
  // initialize SPI:
  SPI.begin(); 
  SPI.setClockDivider(SPI_CLOCK_DIV32);
  Serial.begin(9600);
  Serial1.begin(19200);
  // Init timer3: Fast PWM mode, 10-bit (0111)
  TCCR3A = 0x03;
  TCCR3B = 0x08 | 0x03; // cs = 3; 1/64 prescaler
  TCCR3C = 0x00;
  TIMSK3 = 0x01; // enable overflow interrupt
}

int parse(char*& buf) {
  int rv = 0;
  while (*buf >= '0' && *buf <= '9') {
    rv *= 10;
    rv += *buf - '0';
    buf++;
  }
  return rv;
}

int hex(char h) {
  if (h >= '0' && h <= '9') {
    return h-'0';
  }
  if (h >= 'a' && h <= 'f') {
    return (h-'a')+10;
  }
  if (h >= 'A' && h <= 'F') {
    return (h-'A')+10;
  }
  return 0;
}

void exec(char *buf) {
  char cmd = buf[0];
  switch(cmd) {
    case 'I':
      Serial.println("teensy");
      break;
    case 'r':
      Serial.println("Read on other teensy.");     
      break;
    case 'm':
      {
        buf++;
        boolean escaped = false;
        while (*buf != '\0') {
          if (escaped) {
            if (*buf == 'n') Serial1.write('\n');
            else if (*buf == 'r') Serial1.write('\r');
            else if (*buf == 'x') {
              buf++;
              if (*buf == 0) break;
              int x = hex(*(buf++));
              if (*buf == 0) break;
              x *= 16;
              x += hex(*buf);
              Serial1.write(x); }
            else Serial1.write(*buf);
            escaped = false;
          }
          else if (*buf == '\\') {
            escaped = true;
          } else {
            Serial1.write(*buf);
          }
          buf++;
        }
      }
      break;
    case 'l':
      {
        buf++;
        int i = parse(buf);
        if (*buf != ':') break; // abort
        buf++;
        int j = parse(buf);
        l.setLED(i,(LEDState)j);
      }
      break;
    case 'i':
      {
        buf++;
        int i = parse(buf);
        if (*buf != ':') break; // abort
        buf++;
        int j = parse(buf);
        l.setIlluminated(i,(LEDState)j);
      }
      break;
  }
}

const int BUFSZ = 500;
int i = 0;
char buf[BUFSZ];
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
      if (bidx > BUFSZ-1) bidx = BUFSZ-1;
    }
  }
}

volatile uint8_t cycle = 0;
ISR(TIMER3_OVF_vect) {
  l.show(cycle++);
}
