from chemios.components import PumpControl
import serial
import time
import json
import pytest

# See https://faradayrf.com/unit-testing-pyserial-code/

def import_module(name):
    '''Import a module from a string'''
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod 

def compare(s, t):
    '''Compare two lists that are unorderable and unhasable
    Yields True if the lists are the same
    '''
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t


@pytest.mark.parametrize('pump_manfuacturer', ['HarvardApparatus', 
                                               'Chemyx', 
                                               'NewEra'])
def test_Methods(pump_manufacturer):
    """Test that Each Pump has the corrrect methods"""
    
    methods = ['run', 'set_rate', 'stop', 'get_info', 'configure']
    module_name = "PumpControl.{}".format(pump_manufacturer)
    pump  = import_module(module_name)
    pump_methods = []
    #Check all attributes that are not protected 
    # i.e. the don't start with __
    for attr in dir(pump):
        if attr.rstrip('__') == attr:
            pump_methods.append(attr)
    success = compare(pump_methods, methods)
    assert success == True

@pytest.mark.parametrize('model',['PhD-Ultra'])
@pyteest.mark.parametrize()
def test_HarvardApparatus(model):
    ser = create_serial_port() #automatically imported form conftest

    pump =  PumpControl.HarvardApparatus(model, 1, )

       



  
