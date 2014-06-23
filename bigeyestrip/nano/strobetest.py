from __future__ import division
import serial, time, math

port = serial.Serial('/dev/ttyUSB0', baudrate=115200)
time.sleep(2) # arduino reset

while True:
    t1 = time.time()
    port.write('\x60\x00' + ('\xff\xff\xff' * 50))
    port.flush()
    print 'first', 1000 * (time.time() - t1)
    time.sleep(.00)
    port.write('\x60\x00' + ('\x00\x00\x00' * 50))
    port.flush()
    print ' both', 1000 * (time.time() - t1)
    time.sleep(.2)

    
