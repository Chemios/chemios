from chemiosbrain.pump_control import Pump
from chemiosbrain.utils import serial_write, sio_write
import serial
import sys
import json
import time
import io
import logging

#Get command line arguments
if len(sys.argv) < 4 :
    raise ValueError('Pass in serial port, baud rate, and pump model via command line arguments')
serial_port = sys.argv[1]
baud = sys.argv[2]
model = sys.argv[3]
print("Connecting over port " + serial_port + " at baud rate " + baud)

#Set up logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

#et up serial
ser = serial.Serial(serial_port, baud, timeout=0.1)
# output = sio_write(sio, 'status\x0D', True, timeout = 10)
# print(output)

#Class for stopping pump on ctrl+c
class CleanExit(object):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is KeyboardInterrupt:
            pump1.stop()

#Syringe configuration
rate_limits =  {
                "min_rate": 5.22802,
                "max_rate": 17006.43359
}
syringe_type = {"code": "hm3", "volume": [10, "ml"]}

pump1 = Pump(model=model,address=1, syringe_type=syringe_type, ser=ser)

rate = {'value': 250, 'units': 'UM'}
pump1.set_rate(rate, "INF")
with CleanExit():
    time.sleep(2)
    pump1.run()
    print("Infusing at {} {}.".format(rate['value'],rate['units']))
    while True:
        pass


# rate = {'value': 0.5, 'units': 'UM'}
# pump1.set_rate(rate, "INF")
# pump1.run()
# print("Infusing at {} {}.".format(rate['value'],rate['units']))
# time.sleep(5)
# pump1.stop()
# ser.close()
