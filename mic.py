from __future__ import division
from lightstrip import LightStrip
import time, math, struct, array, threading
import alsaaudio

strip = LightStrip()

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

currentLevel = 0
prevs = []
class Output(threading.Thread):
    def run(self):
        global prevs
        while True:
            prevs = (prevs + [currentLevel])[-config['avgPrevs']:]
            avg = sum(prevs) / len(prevs)
            y = max(0, min(1, (avg - config['levelOffset']) /
                           config['levelMax'])) * 15
            strength = 255 * (config['minStrength'] +
                              y / 15 * (1 - config['minStrength']))
            pts = []
            for x in range(15):
                f = x / 15
                pts.append(((strength * f, strength * (1 - f), 0)
                            if x < y else
                            config['rest']))
            strip.send(pts)
            time.sleep(config['outSleep'])

out = Output()
out.start()

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




