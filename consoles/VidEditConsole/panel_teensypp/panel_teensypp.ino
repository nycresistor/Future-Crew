
// mapping for keypresses for illuminated buttons
const int ILLUM_COUNT = 25;
int illum_keys[ILLUM_COUNT] = {
  8, 
  4, 5, 11, 6,
  9, 32, 10,
  16, 15, 14, 17, 0,
  13, 18, 12, 19, 26, 27, 24, 23, 25, 22, 21, 20
};

void setup() {
  Serial.begin(19200);
  for (int i =0; i < ILLUM_COUNT; i++) {
    pinMode(illum_keys[i],INPUT);
  }
}

void readKeys() {
  for (int i =0; i < ILLUM_COUNT; i++) {
    Serial.print((digitalRead(illum_keys[i]) == HIGH)?"1":"0");
  }
  Serial.println();
}

void exec(char *buf) {
  char cmd = buf[0];
  switch(cmd) {
    case 'I':
      Serial.println("teensypp");
      break;
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
}

