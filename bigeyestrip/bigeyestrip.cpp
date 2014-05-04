#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#define USB_CFG_DEVICE_NAME     'D','i','g','i','B','l','i','n','k'
#define USB_CFG_DEVICE_NAME_LEN 9
#include <DigiUSB.h>

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_RGB     Pixels are wired for RGB bitstream
//   NEO_GRB     Pixels are wired for GRB bitstream
//   NEO_KHZ400  400 KHz bitstream (e.g. FLORA pixels)
//   NEO_KHZ800  800 KHz bitstream (e.g. High Density LED strip)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(3, 5, NEO_GRB + NEO_KHZ800);

const int debugLed = 1;

int main(void) {
  init();
  pinMode(debugLed, OUTPUT);
  strip.begin();
  
  uint32_t red = strip.Color(255,0,0), black = strip.Color(0,0,0);
  strip.setPixelColor(0,   red); strip.show(); delay(100);
  strip.setPixelColor(0, black); strip.show(); delay(100);
  strip.setPixelColor(0,   red); strip.show(); delay(100);
  strip.setPixelColor(0, black); strip.show(); delay(100);
  DigiUSB.begin();
  DigiUSB.refresh();
 
  uint8_t head, i, r, g, b;
  while (1) {
    digitalWrite(debugLed, 0);
    while (DigiUSB.available() <= 0){
      DigiUSB.refresh();
      delay(1);
    }

    head = DigiUSB.read();
    digitalWrite(debugLed, 1);

    if (head != 0x60) {
      continue;
    }
    for (i=0; i < strip.numPixels(); i++) {
      while (!DigiUSB.available()) DigiUSB.refresh(); r = DigiUSB.read();  
      while (!DigiUSB.available()) DigiUSB.refresh(); g = DigiUSB.read();  
      while (!DigiUSB.available()) DigiUSB.refresh(); b = DigiUSB.read();  
      strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show(); 
  }
}

