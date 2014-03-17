from __future__ import division
import sys, wave, audioop
import cyclone.web
import cyclone.websocket
from twisted.python import log
from twisted.internet import reactor, task

sys.path.append("/usr/lib/python2.7/dist-packages")
import pyaudio
import numpy


clients = []

class Sound(cyclone.websocket.WebSocketHandler):
    def connectionMade(self, *args, **kwargs):
        log.msg("ws opened")
        clients.append(self)

    def connectionLost(self, reason):
        log.msg("ws closed")
        clients.remove(self)

    def messageReceived(self, message):
        log.msg("got message %s" % message)
        self.sendMessage(message)

class PushSound(object):
    def __init__(self):
        song = sys.argv[1]
        self.wavs = [
            wave.open('%s/wav/basse.wav' % song),
            wave.open('%s/wav/batterie.wav' % song),
            wave.open('%s/wav/guitare.wav' % song),
            wave.open('%s/wav/voix.wav' % song),
        ]

        self.sampwidth = self.wavs[0].getsampwidth()
        
        self.p = pyaudio.PyAudio()
        print 'width', 
        stream = self.p.open(
            format=self.p.get_format_from_width(self.sampwidth),
            channels=self.wavs[0].getnchannels(),
            rate=self.wavs[0].getframerate(),
            output=True,
            stream_callback=self.callback)

        stream.start_stream()

    def callback(self, in_data, frame_count, time_info, status):
        datas = [w.readframes(frame_count) for w in self.wavs]

        accum = numpy.zeros((frame_count * 2,), numpy.int16)
        
        msg = {}
        for name, data in zip(['bass', 'drums', 'guitar', 'voice'], datas):
            peakValue = audioop.max(data, self.sampwidth)
            peakFrac = peakValue / (1 << (8 * self.sampwidth))
            msg[name] = peakFrac
            arr = numpy.fromstring(data, numpy.int16)
            accum += arr * .7


        msg['chan4'] = .5 * (msg['drums'] + msg['guitar'])
        msg['chan5'] = .5 * (msg['voice'] + msg['guitar'])
        for cl in clients:
            cl.sendMessage(msg)
        #import ipdb;ipdb.set_trace()
            
        return (accum.tostring(), pyaudio.paContinue)


log.startLogging(sys.stdout)
ps = PushSound()
reactor.listenTCP(3001, cyclone.web.Application([
    (r'/sound', Sound),
    ]))
reactor.run()
