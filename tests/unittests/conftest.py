import pytest
import serial

class SerialTestClass(object):
    """A serial port test class using a mock port"""
    def __init__(self):
        self._port = "loop://"
        self._timeout = 0
        self._baudrate = 9600
        self.ser = \
            serial.serial_for_url(url=self._port,
                                  timeout=self._timeout,
                                  baudrate=self._baudrate)

#Only invovke the create_serial_port once per module
@pytest.fixture(scope='module')
def create_serial_port():
    '''Create a mock serial port'''
    ser  = SerialTestClass()
    my_ser = ser.ser
    return my_ser