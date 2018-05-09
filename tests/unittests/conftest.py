import pytest
import serial

class SerialTestClass(object):
    """A serial port test class using a mock port"""
    def __init__(self):
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

#Only invovke the create_serial_port once per module
@pytest.fixture(scope='module')
def create_serial_port(cmd):
    '''Create a mock serial port'''
    ser  = SerialTestClass()
    my_ser = ser.ser
    return my_ser