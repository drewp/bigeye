#bin/python
from __future__ import division
import sys, time, os, traceback, re

import serial
sys.path.append('/usr/lib/python2.7/dist-packages') # PIL, twisted
from PIL import Image
from twisted.internet import reactor, inotify, task
from twisted.python import filepath
import numpy

class Player(object):
    def __init__(self, imagePath, frameOut):
        self.imagePath, self.frameOut = imagePath, frameOut
        self.setRate(30)

        # not working
        self.inotify = inotify.INotify()
        self.inotify.watch(filepath.FilePath(self.imagePath).parent(),
                           inotify.IN_WATCH_MASK,
                           callbacks=[self.reloadImage])

        # fallback from inotify
        task.LoopingCall(self.checkMtime).start(.2)
        
        self.reloadImage()
        
    def checkMtime(self):
        old = getattr(self, 'mtime', 0)
        new = os.path.getmtime(self.imagePath)
        if new != old:
            self.mtime = new
            try:
                self.reloadImage()
            except Exception:
                traceback.print_exc()

    def setRate(self, pxPerSec):
        print "new rate", pxPerSec
        self.pxPerSec = pxPerSec
        
    def reloadImage(self, *args):
        print "reloading %s" % self.imagePath
        i = Image.open(self.imagePath)
        self.img = numpy.asarray(i)
        print self.img.shape

    def step(self):
        now = time.time()
        x = int((now * self.pxPerSec) % self.img.shape[1])
        col = self.img[::-1,x,:]
        self.frameOut(col)

if __name__ == "__main__":
    leds = int(re.search('NeoPixel.(\d+)', open('nanostrip.cpp').read()).group(1))
    port = serial.Serial('/dev/ttyUSB0', baudrate=115200)
    time.sleep(2) # arduino reset
    filename = '../colors.png'

    def frameOut(colors):
        port.write('\x60\x00')
        for color in colors:
            port.write(chr(int(color[2])) +
                       chr(int(color[0])) +
                       chr(int(color[1])))
        port.flush()
    
    player = Player(filename, frameOut)
    player.setRate(30)
    def loop():
        player.step()
        reactor.callLater(.01, loop)
    loop()
    reactor.run()
