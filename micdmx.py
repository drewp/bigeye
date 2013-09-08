


from __future__ import division
import sys, random, json, httplib, logging
sys.path.append("../light9")
sys.path.append("../light9/bin")
from run_local import log
sys.path.append("/usr/lib/pymodules/python2.7") # for alsaaudio
import time, math, struct, array, threading, colorsys
import alsaaudio
import cyclone.web, cyclone.httpclient, cyclone.websocket

from light9 import dmxclient

inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 'default')
inp.setchannels(1)
inp.setrate(44100)
inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
inp.setperiodsize(80)

config = {
    'rest' : (0, 0, 2),
    'avgPrevs' : 1,
    'levelOffset' : 0,
    'levelMax' : 1,
    'minStrength' : .02,
    'outSleep' : .01,
    'gamma': 2,
    }
state = {
    'dominantHue':0,
    'lastHueTime':0,
    }
firstDmxChannel = 73

currentLevel = 0
prevs = []
envPrevs = [0,1] # recent values for auto-normalization
envLo = 0
envHi = 1
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
                
            currentLevel = max(m, currentLevel * .9998)

            if t > lastPrint + .1:
                #print nframes, m, "*" * int(m/300)
                lastPrint = t

def writeOut():
    global prevs, envPrevs, envLo, envHi
    now = time.time()

    envPrevs = (envPrevs + [currentLevel])[-50:]
    
    prevs = (prevs + [currentLevel])[-config['avgPrevs']:]
    avg = sum(prevs) / len(prevs)

    yEnv = max(0, avg - envLo) / (envHi - envLo)

    envLo = min(envPrevs)
    envHi = max(envPrevs)
    
    
    y = max(0, min(1, (yEnv + config['levelOffset']) /
                   config['levelMax']))
    y = math.pow(y, config['gamma'])
    if y > .8 and now > state['lastHueTime'] + .3:
        state['dominantHue'] = .5 - state['dominantHue']#random.random()
        state['lastHueTime'] = time.time()
        print "hue", state['dominantHue']

    chans = [0] * 90

    h = state['dominantHue'] + y / 5
    chans[73-1:76-1] = list(colorsys.hsv_to_rgb(h, 1, y))
    chans[80-1:83-1] = list(colorsys.hsv_to_rgb(h, 1, y))
    chans[88-1:91-1] = list(colorsys.hsv_to_rgb(h, .4, y)) # center
    chans[87-1] = .84

    dmxclient.outputlevels(chans, twisted=True)

audio = Input()
audio.start()

liveClients = set()
def sendToLiveClients(d=None, asJson=None):
    j = asJson or json.dumps(d)
    for c in liveClients:
        c.sendMessage(j)

class Live(cyclone.websocket.WebSocketHandler):

    def connectionMade(self, *args, **kwargs):
        log.info("websocket opened")
        liveClients.add(self)

    def connectionLost(self, reason):
        log.info("websocket closed")
        liveClients.remove(self)

    def messageReceived(self, message):
        log.info("got message %s" % message)
        if message == "getWaveform":
            sendToLiveClients({
                'points': [int(100 * s / 32768) for s in envPrevs]})

class Params(cyclone.web.RequestHandler):
    def get(self):
        self.write(json.dumps(config))

class Param(cyclone.web.RequestHandler):
    def put(self, name):
        config[name] = float(self.request.body)
        self.set_status(httplib.ACCEPTED)

log.setLevel(logging.DEBUG)
from twisted.internet import reactor, task
task.LoopingCall(writeOut).start(config['outSleep'])
port = 9991
reactor.listenTCP(port, cyclone.web.Application(handlers=[
    (r'/live', Live),
    (r'/params', Params),
    (r'/params/(.*)', Param),

    (r'/(.*)', cyclone.web.StaticFileHandler,
     {"path" : "www", "default_filename" : "index.html"}),
    
], debug=True))

reactor.run()
