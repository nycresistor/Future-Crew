void setup() {
  for (int i =0; i < 11; i++) {
    pinMode(i, INPUT_PULLUP);
  }
  Serial.begin(19200);
  Serial.println("initialized serial");
  analogReadRes(10);
  analogReadAveraging(5);
  analogReference(DEFAULT);
}


void readValues() {
  for (int i =0; i < 11; i++) {
      int j = analogRead(i);
      if (digitalRead(i) == LOW) {
        Serial.print("0/");
      } else {
        Serial.print("1/");
      }
      Serial.print(j);
      Serial.print(" ");
  }
  Serial.println();
}


void exec(char *buf) {
  char cmd = buf[0];
  switch(cmd) {
    case 'I':
      Serial.println("teensy3");
      break;
    case 'r':
      readValues();
      break;
  }
}

const int BUFSZ = 500;
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

