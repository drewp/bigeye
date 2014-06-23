from __future__ import division
import serial, time, math

port = serial.Serial('/dev/ttyUSB0', baudrate=115200)
time.sleep(2) # arduino reset
port.write('\x60\x01\x00')
while True:
    v = math.sin(time.time()) / 2 + .5
    print v
    port.write('\x60\x01' + chr(int(255 * v)))
    time.sleep(.02)

    
