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
    while 1:
        if audioFrame == lastAudioFrame:
            continue
        lastAudioFrame = audioFrame
        colors = []

        levels = numpy.clip((numpy.array(latestAudio[1][:50]) / 40 - .3) * 2, 0, 1) ** 2
        if accum is None:
            accum = levels
        accum = levels#.3 * accum + .7 * levels
        levelAdj = numpy.clip((latestAudio[0] - 1200) / 6000, 0, 1)
        print levelAdj
        for pos in range(leds):
            # _______
            #        \
            #         \_______
            #        l
            bright = 1
            if pos / leds > levelAdj:
                bright = 0
            colors.append([accum[pos] * bright, accum[pos] * bright, bright * .1])

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
