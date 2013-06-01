/** 
*   Arduino Control Code for a Button Console
*   FUTUREEEE CRRREWWWW!!!
*   Author: Guy Dickinson <guy@gdickinson.co.uk> | @gdickinson
*   
*   This code is designed to be run as a Teensyduino but could easily be used on an Arduino
*   which has been wired up correctly. LED pins are configured to SINK current.
*   Button digital inputs require a pullup.
**/
#include <string.h>
#define NUM_BUTTONS 10

char stateBuffer[64] = {};

// Buttons are numbered 0 to 9, from left to right. Each button has an LED and a digital input.
int button_pins[NUM_BUTTONS] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
int led_pins[NUM_BUTTONS] = {21, 19, 18, 17, 16, 15, 14, 13, 12, 22};

void setup() {
  Serial.begin(9600);

  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(button_pins[i], INPUT_PULLUP);
    pinMode(led_pins[i], OUTPUT);
  }
}

void lightIfPressed(int buttonIdx, int buttonState) {
  if (buttonState == LOW) {
    digitalWrite(led_pins[buttonIdx], LOW);
  } else {
    digitalWrite(led_pins[buttonIdx], HIGH);
  }
}

void buttonLoop() {
  for (int i = 0; i < NUM_BUTTONS; i++) {
    int state = digitalRead(button_pins[i]);
    lightIfPressed(i, state);
  }
}

void sendButtonState(int idx, int state) {
  int buffOffset = 0;
}

void loop() {
  buttonLoop();  
}