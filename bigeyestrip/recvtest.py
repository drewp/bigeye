#bin/python
from __future__ import division
import sys, time, colorsys, math, random
sys.path.append("DigisparkExamplePrograms/Python/DigiUSB/source")

from arduino.usbdevice import ArduinoUsbDevice

if __name__ == "__main__":
    theDevice = ArduinoUsbDevice(idVendor=0x16c0, idProduct=0x05df)
    print theDevice.productName, theDevice.manufacturer

    t1 = time.time()
    frames = 0

    def retryWrite(b):
        try:
            theDevice.write(b)
        except Exception, e:
            print e
            time.sleep(.01)
            retryWrite(b)
    hue = .1
    while 1:
        now = time.time()
        colors = []
        amp = math.sin(now * 6.28 * .8) / 2 + .5
        if amp < .02:
            hue = random.random()
        leds = 26
        for pos in range(leds):
            if amp - pos / leds < .2:
                bright = 1
                sat = .5
            else:
                bright = .1
                sat = 1
            colors.append(colorsys.hsv_to_rgb(hue,#(now * .3 + pos / 3) % 1.0,
                                              sat,
                                              bright * min(1, max(0, amp - pos / leds))))
       
        retryWrite(0x60)
        for color in colors:
            retryWrite(int(255 * color[0]))
            retryWrite(int(255 * color[1]))
            retryWrite(int(255 * color[2]))
        frames += 1
        if frames > 100:
            print "fps: %.1f" % (frames / (time.time() - t1))
            frames = 0
            t1 = time.time()

