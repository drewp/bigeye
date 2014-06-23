#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_RGB     Pixels are wired for RGB bitstream
//   NEO_GRB     Pixels are wired for GRB bitstream
//   NEO_KHZ400  400 KHz bitstream (e.g. FLORA pixels)
//   NEO_KHZ800  800 KHz bitstream (e.g. High Density LED strip)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(50, 5, NEO_RGB + NEO_KHZ800);

// max about 26 with malloc; 36 works with a static array in the class

#define debugLed 13
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
  Serial.begin(115200);

 
  uint8_t i,r,g,b;
  while (1) {
    while (Serial.available() <= 2) {
    }
    i = Serial.read();
    if (i != 0x60) {
      continue;
    }
    i = Serial.read(); // command
    if (i == 0) { // set strip: 0x60 0x00 <numPixels * 3 bytes>
      digitalWrite(debugLed, 1);
      for (i=0; i < strip.numPixels(); i++) {
        while (Serial.available() < 3) {
        }
        r = Serial.read();
        g = Serial.read();
        b = Serial.read();
        strip.setPixelColor(i, strip.Color(g, r, b));
      }
      strip.show();

      digitalWrite(debugLed, 0);
    } else if (i == 1) { // set pwm on D3: 0x60 0x01 <level>
      while (Serial.available() < 1) {
      }
      analogWrite(3, Serial.read());
    } else {
        // unknown command
    }
  }
}
