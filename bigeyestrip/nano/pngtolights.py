#bin/python
from __future__ import division
import sys, time, math, re, os


import serial
sys.path.append('/usr/lib/python2.7/dist-packages')
from PIL import Image

if __name__ == "__main__":
    leds = int(re.search('NeoPixel.(\d+)', open('nanostrip.cpp').read()).group(1))
    port = serial.Serial('/dev/ttyUSB0', baudrate=115200)
    time.sleep(2) # arduino reset
    filename = '../colors.png'
    lastTime = 0
    while 1:
        mtime = os.path.getmtime(filename)
        if mtime == lastTime:
            time.sleep(.5)
            continue
        lastTime = mtime
        img = Image.open(filename)
        print "Sending update"
        port.write('\x60')
        port.write(map(chr, sum([(r,g,b) for g,b,r in img.getdata()], ())))
        port.flush()


