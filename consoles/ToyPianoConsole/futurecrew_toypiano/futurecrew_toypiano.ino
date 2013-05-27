// wire all 25 teensy 2.0 inputs as piano keys
// -- sends keypresses or MIDI notes depending on whether MIDI_MODE is defined below.

// requires debounce library
// http://playground.arduino.cc/code/bounce
#include <Bounce.h>

// Fix bug with arduino IDE preprocessor - insert me on top of your arduino-code
// From: http://www.a-control.de/arduino-fehler/?lang=en (now dead)
// I found it at http://subethasoftware.com/2013/04/09/arduino-compiler-problem-with-ifdefs-solved/
#if 1
__asm volatile ("nop");
#endif
// end of fix


// comment out for keyboard mode, uncomment for midi mode
#define MIDI_MODE


#define NUM_KEYS 25
#define DEBOUNCE_MSEC 20


#ifdef MIDI_MODE

int lownote = 48;

#else

char keys[NUM_KEYS] = {
  'z','s','x','d','c', 
  'v','g','b','h','n','j','m',
  'q','2','w','3','e',
  'r','5','t','6','y','7','u','i'
};

#endif
  
  
Bounce *bounce[NUM_KEYS];


void setup() {
  for (int i=0; i<NUM_KEYS; i++) {
    pinMode(i, INPUT_PULLUP);
    bounce[i] = new Bounce( i, DEBOUNCE_MSEC );
  }

}

void loop() {
  // Update the debouncers
  for (int i=0; i<NUM_KEYS; i++) {
    bounce[i]->update();
    if (bounce[i]->fallingEdge()) {
#ifdef MIDI_MODE
      usbMIDI.sendNoteOn(lownote+i, 127, 1);
#else
      Keyboard.print(keys[i]);
#endif
    }
    
#ifdef MIDI_MODE
    if (bounce[i]->risingEdge()) {
      usbMIDI.sendNoteOff(lownote+i, 0, 1);
    }
#endif
  }
  
 
}

