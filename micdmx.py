from __future__ import division
import sys
sys.path.append("../light9")
sys.path.append("../light9/bin")
from run_local import log
sys.path.append("/usr/lib/pymodules/python2.7") # for alsaaudio
import time, math, struct, array, threading, colorsys
import alsaaudio
from light9 import dmxclient



inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 'default')
inp.setchannels(1)
inp.setrate(44100)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(80)

config = {
    'rest' : (0, 0, 10),
    'avgPrevs' : 1,
    'levelOffset' : 0,
    'levelMax' : 8000,
    'minStrength' : .02,
    'outSleep' : .01,
    }
firstDmxChannel = 10

currentLevel = 0
prevs = []
class Input(threading.Thread):
    def run(self):
        global currentLevel
        lastPrint = 0
        while True:
            t = time.time()
            nframes, data = inp.read()
            if nframes == 0:
                continue
            m = 0
            for v in array.array("h", data):
                m = max(abs(v), m)

            currentLevel = m
            if t > lastPrint + .1:
                print nframes, m, "*" * int(m/300)
                lastPrint = t


def writeOut():
    global prevs

    prevs = (prevs + [currentLevel])[-config['avgPrevs']:]
    avg = sum(prevs) / len(prevs)           
    y = max(0, min(1, (avg - config['levelOffset']) /
                   config['levelMax']))

    chans = list(colorsys.hsv_to_rgb(1, 1, y))

    dmxclient.outputlevels([0] * (firstDmxChannel - 1) + chans, twisted=True)

audio = Input()
audio.start()


from twisted.internet import reactor, task
task.LoopingCall(writeOut).start(config['outSleep'])


reactor.run()
