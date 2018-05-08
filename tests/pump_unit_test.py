from pump_control import pump
import serial
import time
import json
import unnittest

# See https://faradayrf.com/unit-testing-pyserial-code/


class SerialTestClass(object):
    """A serial port test class using a mock port"""
    def __init__(self):
        """Creates a mock serial port which is a loopback object"""
        self._port = "loop://"
        self._timeout = 0
        self._baudrate = 9600
        self._stopbits = 'STOPBITS_ONE'
        self._parity = 'PARITY_NONE'
        self.ser = \
            serial.serial_for_url(url=self._port,
                                  timeout=self._timeout,
                                  baudrate=self._baudrate,
                                  stopbits = self._stopbits,
                                  parity = self._parity)

class pumpTests(SerialTestClass):
    def __init__(self, NE1000=None, DIY=None):
        self.NE1000 = pump('NE-1000', 0, ser)
        self.NE1000.set_diameter(100)
        self.DIY = pump('DIY', 0, ser)


    def test_info():
        info = self.NE1000.get_info()
        self.assertEqual(info['model'], 'NE-1000')
        self.assertEqual(info['address'], 0)
        self.assertEqual(info['syringe_diameter'], 100)

    def test_run():


if __name == '__main__':
    unnittest.main()
