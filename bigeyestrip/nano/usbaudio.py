from __future__ import division
import pyaudio, time, sys
sys.path.append('/usr/lib/python2.7/dist-packages') # numpy
sys.path.append('/usr/lib/pymodules/python2.7') # numpy on pi
import numpy

class AudioIn(object):
    def __init__(self, onData, deviceSubstring='HD-4110'):
        self.onData = onData
        p = pyaudio.PyAudio()

        rate = 44100 // 2

        self.stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=rate,
            input=True,
            input_device_index=self.inputDeviceIndex(p, deviceSubstring),
            frames_per_buffer=512,
            stream_callback=self.ondata,
        )
        print "reading audio..."

    def inputDeviceIndex(self, p, deviceSubstring):
        for dev in range(p.get_device_count()):
            info = p.get_device_info_by_index(dev)
            if info['maxInputChannels'] > 0 and deviceSubstring in info['name']:
                print "using %s" % info
                return dev

        raise ValueError("no inputs")
        
    def ondata(self, data, frame_count, time_info, status):
        # getting lots of status=inputoverflow
        samples = numpy.fromstring(data, dtype=numpy.int16)
        # see http://www.raspberrypi.org/forums/viewtopic.php?p=314087
        fourier = numpy.fft.rfft(samples)
        power = numpy.log10(numpy.abs(fourier)) ** 2
        #power = samples
        self.onData(max(abs(samples)), power)
        return (None, pyaudio.paContinue)

if __name__ == '__main__':
   
    def onData(level, power):
        rows = 10
        for row in range(rows):
            for i in range(0, len(power) // 4):
                if (power[i] / 40) ** 2 > (1 - row / rows):
                    sys.stdout.write('| ')
                else:
                    sys.stdout.write('  ')
            sys.stdout.write('\n')
        print level, '*' * (level // 320)
    audioIn = AudioIn(onData)
    while 1:
        time.sleep(1)
