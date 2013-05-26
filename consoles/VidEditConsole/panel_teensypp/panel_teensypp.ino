
// mapping for keypresses for illuminated buttons
const int ILLUM_COUNT = 25;
int illum_keys[ILLUM_COUNT] = {
  27,  0,  4,  5,  6, 32,  8,  9,
  10, 11, 12, 13, 14, 15, 16, 17,
  18, 19, 20, 21, 22, 23, 24, 25, 
  26
};

void setup() {
  for (int i =0; i < ILLUM_COUNT; i++) {
    pinMode(illum_keys[i],INPUT);
  }
}

void readKeys() {
  for (int i =0; i < ILLUM_COUNT; i++) {
    if (digitalRead(illum_keys[i]) == HIGH) { 
      Serial.print(illum_keys[i]);
      Serial.print(" ");
    }
  }
  Serial.println();
}

void exec(char *buf) {
  char cmd = buf[0];
  switch(cmd) {
    case 'r':
      readKeys();
      break;
  }
}

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
  delay(100);
  readKeys();
}

