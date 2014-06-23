#bin/python
from __future__ import division
import sys, time, math, re

import serial
from usbaudio import AudioIn
import numpy

if __name__ == "__main__":
    leds = int(re.search('NeoPixel.(\d+)', open('nanostrip.cpp').read()).group(1))
    port = serial.Serial('/dev/ttyUSB0', baudrate=115200)

    audioFrame = 0
    latestAudio = 0, []
    def onData(level, power):
        global latestAudio, audioFrame
        latestAudio = level, power
        audioFrame += 1

    audioIn = AudioIn(onData)

    t1 = time.time()
    frames = 0
    lastAudioFrame = 0
    accum = None
    levelAdj = 0
    while 1:
        if audioFrame == lastAudioFrame:
            continue
        lastAudioFrame = audioFrame
        #print "new audio", latestAudio[0]
        colors = []


        
        lowFreqs = latestAudio[1][:50]
        levels = numpy.array([lowFreqs[i//3] for i in range(150)])
        levels = numpy.absolute(levels)
        print levels
        levels = numpy.clip((levels / 60 - .1) * 1, 0, 1) ** 2
        if accum is None:
            accum = levels
        accum = 0 * accum + 1 * levels
        newLevelAdj = numpy.clip((latestAudio[0] - 1200) / 9000, 0, 1)
        levelAdj = .2 * max(levelAdj, newLevelAdj) + .8 * newLevelAdj
        print levelAdj
        for pos in range(leds):
            # _______
            #        \
            #         \_______
            #        l
            bright = 1
            if pos / leds > levelAdj:
                bright = 0
            colors.append([accum[pos] * bright,
                           accum[pos] * bright,
                           bright * .1])

        port.write('\x60')
        for color in colors:
            port.write(chr(int(255 * color[2])) +
                       chr(int(255 * color[0])) +
                       chr(int(255 * color[1])))
        port.flush()
        time.sleep(.015)
        frames += 1
        if frames > 100:
            print "fps: %.1f" % (frames / (time.time() - t1))
            frames = 0
            t1 = time.time()
