# thanks, http://christopherpoole.github.io/developing-for-the-digispark-without-the-arduino-ide/

DIGISPARK_DIR = DigisparkArduinoIntegration-master

TARGET                 = main
#DIGISPARK_LIBS         = 
MCU                    = attiny85
F_CPU                  = 16500000L


LOCAL_LIBS = Adafruit_NeoPixel DigisparkArduinoIntegration-master/libraries/DigisparkUSB
OTHER_OBJS = build-cli/libs/Adafruit_NeoPixel.o 
#	build-cli/libs/DigisparkUSB/oddebug.o \
#	build-cli/libs/DigisparkUSB/osccal.o \
#	build-cli/libs/DigisparkUSB/usbdrvasm.o \
#	build-cli/libs/DigisparkUSB/usbdrv.o

MICRONUCLEUS_DIR = micronucleus-t85/commandline
include Arduino-local.mk
