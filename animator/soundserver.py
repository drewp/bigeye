from __future__ import division
import sys, wave, audioop, collections
import cyclone.web
import cyclone.websocket
from twisted.python import log
from twisted.internet import reactor, task

sys.path.append("/usr/lib/python2.7/dist-packages")
import pyaudio
import numpy
import pygame.midi

clients = collections.defaultdict(list) # Class name : list of clients

class Sound(cyclone.websocket.WebSocketHandler):
    def connectionMade(self, *args, **kwargs):
        log.msg("ws opened %s" % self.__class__)
        clients[self.__class__.__name__].append(self)

    def connectionLost(self, reason):
        log.msg("ws closed")
        clients[self.__class__.__name__].remove(self)

    def messageReceived(self, message):
        log.msg("got message %s" % message)
        self.sendMessage(message)

class Midi(Sound):
    pass

class WatchMidi(object):
    def __init__(self):
        pygame.midi.init()

        dev = self.findQuneo()
        self.inp = pygame.midi.Input(dev)
        task.LoopingCall(self.step).start(.05)
        
    def step(self):
        if not self.inp.poll():
            return
        for ev in self.inp.read(999):
            for cl in clients['Midi']:
                print ev
                cl.sendMessage({'status': ev[0][0],
                                'data1': ev[0][1],
                                'data2': ev[0][2],
                                'data3': ev[0][3],
                            })
            
        
    def findQuneo(self):
        for dev in range(pygame.midi.get_count()):
            interf, name, isInput, isOutput, opened = pygame.midi.get_device_info(dev)
            if 'QUNEO' in name and isInput:
                return dev
        raise ValueError("didn't find quneo input device")

wm = WatchMidi()
    
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
        for cl in clients.get('Sound', []):
            cl.sendMessage(msg)
            
        return (accum.tostring(), pyaudio.paContinue)


log.startLogging(sys.stdout)
ps = PushSound()
reactor.listenTCP(3001, cyclone.web.Application([
    (r'/sound', Sound),
    (r'/midi', Midi),
    ]))
reactor.run()
