#include <SPI.h>

const int DATA_IN = 18;
const int SH_OUT = 16;
const int ST_OUT = 15;
const int PL_OUT = 14;

void setup() {
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
}

void readKeys() {
  digitalWrite(PL_OUT,LOW);
  digitalWrite(ST_OUT,HIGH);
  digitalWrite(ST_OUT,LOW);
  digitalWrite(PL_OUT,HIGH);
  for (int i = 0; i < 16; i++) {
    digitalWrite(SH_OUT,HIGH);
    Serial.print(digitalRead(DATA_IN));
    digitalWrite(SH_OUT,LOW);
  }
  Serial.println();
  digitalWrite(PL_OUT,LOW);
}

void loop() {
  SPI.transfer(0x55);
  delay(200);
  readKeys();
  SPI.transfer(0xAA);
  delay(200);
  readKeys();
}
