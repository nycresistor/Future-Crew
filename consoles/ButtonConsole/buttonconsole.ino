/** 
*   Arduino Control Code for a Button Console
*   FUTUREEEE CRRREWWWW!!!
*   Author: Guy Dickinson <guy@gdickinson.co.uk> | @gdickinson
*   
*   This code is designed to be run as a Teensyduino but could easily be used on an Arduino
*   which has been wired up correctly.
**/

#define NUM_BUTTONS 10

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

void loop() {
  // Is there any serial input? If so, get it.

  // Post the current button state to the serial output
  
}