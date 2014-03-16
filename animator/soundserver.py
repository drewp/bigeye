from __future__ import division
import wave, audioop
import cyclone.web
import cyclone.websocket
from twisted.python import log
from twisted.internet import reactor, task

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
        self.wav = wave.open('roxanne/wav/batterie.wav')
        self.framerate = self.wav.getframerate()
        task.LoopingCall(self.step).start(1 / 30)

    def step(self):
        frames = self.wav.readframes(int(self.framerate * 1 / 30))
        peakValue = audioop.max(frames, self.wav.getsampwidth())
        peakFrac = peakValue / (1 << (8 * self.wav.getsampwidth()))

        for cl in clients:
            cl.sendMessage({'drums':peakFrac,})


ps = PushSound()
reactor.listenTCP(3001, cyclone.web.Application([
    (r'/sound', Sound),
    ]))
reactor.run()
