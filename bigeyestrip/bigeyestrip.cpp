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
Adafruit_NeoPixel strip = Adafruit_NeoPixel(26, 5, NEO_GRB + NEO_KHZ800);

// max about 26 with malloc; 36 works with a static array in the class

#define debugLed 1
void intro() {
  uint32_t red = strip.Color(255,0,0), black = strip.Color(0,0,0);
  strip.setPixelColor(0,   red); strip.show(); delay(100);
  strip.setPixelColor(0, black); strip.show(); delay(100);
  strip.setPixelColor(0,   red); strip.show(); delay(100);
  strip.setPixelColor(0, black); strip.show(); delay(100);
}
int main(void) {
  init();
  pinMode(debugLed, OUTPUT);
  strip.begin();
  intro(); 
  DigiUSB.begin();
  DigiUSB.refresh();
 
  uint8_t i;
  int r, g, b;
  while (1) {
    digitalWrite(debugLed, 0);
    while (DigiUSB.available() <= 0){
      DigiUSB.refresh();
    }

    i = DigiUSB.read();
    digitalWrite(debugLed, 1);

    if (i != 0x60) {
      continue;
    }
    for (i=0; i < strip.numPixels(); i++) {
      while (DigiUSB.available() < 3) {
        DigiUSB.refresh();
      }
      r = DigiUSB.read();
      g = DigiUSB.read();
      b = DigiUSB.read();
      strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show(); 
  }
}

