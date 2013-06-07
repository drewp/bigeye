# sudo LIGHT9_SHOW=/home/drewp/projects/light9/show/dance2012 padsp python wavein.py

from __future__ import division
from twisted.internet import reactor, task
import time, sys, pygame
sys.path.append("../light9")

from light9.dmxclient import outputlevels

disp = pygame.display.set_mode((256,800))


dsp = open('/dev/dsp')

class Wv(object):
    def __init__(self):
        self.v = 0
        
    def readSample(self):
        dsp.flush()
        b = dsp.read(2)

        x = abs(ord(b[0]) - 128) / 128

        outputlevels([0,0,0,0,0,0,0,0,0,0, x], twisted=True)

        intens = 255 * x
        disp.fill((intens, intens, intens))
        pygame.display.flip()

        #sys.stdout.write('*' * int(180*x) + "\n")
        #sys.stdout.flush()

wv = Wv()
task.LoopingCall(wv.readSample).start(1/20)

reactor.run()
