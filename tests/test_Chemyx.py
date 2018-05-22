from chemios.components.pumps import Chemyx
from chemios.utils import SerialTestClass
#from dummyserial import Serial
import pytest
import logging

#Logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG)
logfile = 'chemios_dev.log'
fileHandler = logging.FileHandler(logfile)
fileHandler.setLevel(logging.DEBUG)
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

@pytest.fixture()
def ser():
    '''Create a mock serial port'''
    ser  = SerialTestClass()
    my_ser = ser.ser
    return my_ser

# @pytest.fixture(scope='module')
# def mock_chemyx():
#     mock_responses = {
#                         'start\x0D': "Pump start running…",
#                         'stop\x0D': "Pump stop!",
#                         'set diameter 1.00\x0D': 'diameter = 1.00',
#                         'set diameter 4.65\x0D': 'diameter = 4.65',
#                         'set rate 10.0\x0D': 'rate = 10.0',
#                         'set rate 100\x0D': 'rate = 100',
#                         'set units 0\x0D': 'units = 0',
#                         'set units 1\x0D': 'units = 1',
#                         'set units 2\x0D': 'units = 2',   
#                         'set units 3\x0D': 'units = 3'                                 
#     }
#     ser = Serial(port='test', 
#                 ds_responses=mock_responses)
#     return ser


@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 200', 
                                   'Fusion 4000', 'Fusion 6000', 
                                   'NanoJet', 'OEM'])
def test_init(ser, model):
    '''Test initialization of chemyx pump'''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    Chemyx(model=model, ser=ser)


@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 200', 
                                   'Fusion 4000', 'Fusion 6000', 
                                   'NanoJet', 'OEM'])
def test_get_info(ser, model):
    '''Test Get info'''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    C = Chemyx(model=model, ser=ser)
    C.get_info()

@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 4000','OEM'])
@pytest.mark.parametrize('manufacturer', ['terumo-japan', 'terumo','sge'])
@pytest.mark.parametrize('volume', [5.0, 10.0])
def test_set_syringe(ser, model, manufacturer, volume):
    '''Test set_sryinge info'''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    C = Chemyx(model=model, ser=ser, 
               syringe_manufacturer=manufacturer, syringe_volume=volume)
    #Reduce retry time for unit tests
    C.retry = 0.01
    C.set_syringe(manufacturer=manufacturer, volume=volume)

@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 4000','OEM'])
def test_rate(ser, model):
    '''Test Run info'''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    C = Chemyx(model=model, ser=ser, 
               syringe_manufacturer='terumo-japan', syringe_volume=1)
    rate = {'value': 20, 'units': 'uL/min'}
    C.set_rate(rate, 'INF')

@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 200', 
                                   'Fusion 4000', 'Fusion 6000', 
                                   'NanoJet', 'OEM'])
def test_run(ser, model):
    '''Test Run info'''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    C = Chemyx(model=model, ser=ser, 
               syringe_manufacturer='terumo-japan', syringe_volume=1)
    rate = {'value': 20, 'units': 'uL/min'}
    C.set_rate(rate, 'INF')
    C.run()


@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 4000','OEM'])
@pytest.mark.parametrize('units', ['mL/min', 'mL/hr', 'uL/min', 'uL/hr'])
def test_set_units(ser, model, units):
    '''Test set_units '''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    C = Chemyx(model=model, ser=ser)
    C.set_units(units)


@pytest.mark.parametrize('model', ['Fusion 100', 'Fusion 4000','OEM'])
def test_stop(ser, model):
    '''Test stop'''
    if model in ['Nanojet', 'OEM']:
        ser.baudrate = 38400
    C = Chemyx(model=model, ser=ser)
    C.stop()

    
    
    

