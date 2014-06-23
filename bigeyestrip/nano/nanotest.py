#bin/python
from __future__ import division
import sys, time, colorsys, math, random, serial, re

if __name__ == "__main__":
    port = serial.Serial('/dev/ttyUSB0', baudrate=115200)

    t1 = time.time()
    frames = 0

    leds = int(re.search('NeoPixel.(\d+)', open('nanostrip.cpp').read()).group(1))
    
    hue = .1
    while 1:
        now = time.time()
        colors = []
        amp = math.sin(now * 6.28 * .4) / 2 + .5
        if amp < .02:
            hue = random.random()
        for pos in range(leds):
            if pos < 100:
                colors.append([0,0,0])
                continue
            if amp - pos / leds < .2:
                bright = 1
                sat = .5
            else:
                bright = .1
                sat = 1
            bright = 1;amp=10
            if 1:
                colors.append(colorsys.hsv_to_rgb(hue,#(now * .3 + pos / 3) % 1.0,
                                                  sat,
                                                  bright * min(1, max(0, amp - pos / leds))))

        port.write('\x60')
        for color in colors:
            port.write(chr(int(255 * color[0])) +
                       chr(int(255 * color[1])) +
                       chr(int(255 * color[2])))
        port.flush()
        time.sleep(.015)
        frames += 1
        if frames > 100:
            print "fps: %.1f" % (frames / (time.time() - t1))
            frames = 0
            t1 = time.time()

