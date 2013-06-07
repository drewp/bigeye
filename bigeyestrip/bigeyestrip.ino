#include <Adafruit_NeoPixel.h>

// Parameter 1 = number of pixels in strip
// Parameter 2 = pin number (most are valid)
// Parameter 3 = pixel type flags, add together as needed:
//   NEO_RGB     Pixels are wired for RGB bitstream
//   NEO_GRB     Pixels are wired for GRB bitstream
//   NEO_KHZ400  400 KHz bitstream (e.g. FLORA pixels)
//   NEO_KHZ800  800 KHz bitstream (e.g. High Density LED strip)
Adafruit_NeoPixel strip = Adafruit_NeoPixel(15, 6, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();
  strip.show(); // Initialize all pixels to 'off'
 
  uint32_t red = strip.Color(255,0,0), black = strip.Color(0,0,0);
  strip.setPixelColor(0,   red); strip.show(); delay(100);
  strip.setPixelColor(0, black); strip.show(); delay(100);
  strip.setPixelColor(0,   red); strip.show(); delay(100);
  strip.setPixelColor(0, black); strip.show(); delay(100);
  
  Serial.begin(115200);
}

void loop() {
  uint8_t head, i, r, g, b;

  head = Serial.read();
  if (head != 0x60) {
    return;
  }
  for (i=0; i < strip.numPixels(); i++) {
    while (!Serial.available()) NULL; r = Serial.read();  
    while (!Serial.available()) NULL; g = Serial.read();  
    while (!Serial.available()) NULL; b = Serial.read();  
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();
}

