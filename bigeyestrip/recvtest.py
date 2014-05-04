#bin/python
from __future__ import division
import sys, time, colorsys, math
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
    while 1:
        now = time.time()
        retryWrite(0x60)
        for pos in range(3):
            color = colorsys.hsv_to_rgb((now * .3 + pos / 3) % 1.0,
                                        1,
                                        math.sin((now + pos / 3) * 6.28 * 2) / 2 + .5)
            retryWrite(int(255 * color[0]))
            retryWrite(int(255 * color[1]))
            retryWrite(int(255 * color[2]))
        frames += 1
        if frames > 100:
            print "fps: %.1f" % (frames / (time.time() - t1))
            frames = 0
            t1 = time.time()

