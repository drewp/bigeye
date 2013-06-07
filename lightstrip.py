from __future__ import division
import time, math
from serial import Serial
class LightStrip(object):
    def __init__(self, port='/dev/ttyUSB0'):
        self.ser = Serial(port=port, baudrate=115200, timeout=1)
        time.sleep(0)  # wait for a arduino reset to pass
        self.ser.flush()
    def send(self, rgbs):
        assert len(rgbs) == 15, rgbs
        packet = "\x60" + ''.join(chr(int(r))+chr(int(g))+chr(int(b)) for r,g,b in rgbs)
        self.ser.write(packet)

if __name__ == '__main__':
    strip = LightStrip()
    for i in range(256):
        y = (math.sin(i / 3) + 1) * 15/2
        strip.send([((0,i,0) if x < y else (150,150,0))for x in range(15)])
        time.sleep(.02)


