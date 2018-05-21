from chemios.components import pumps
import serial
import time
import json
import pytest
import re

# # See https://faradayrf.com/unit-testing-pyserial-code/

# def import_module(name):
#     '''Import a module from a string'''
#     components = name.split('.')
#     mod = __import__(components[0])
#     for comp in components[1:]:
#         mod = getattr(mod, comp)
#     return mod 

# def compare(s, t):
#     '''Compare two lists that are unorderable and unhasable
#     Yields True if the lists are the same
#     '''
#     t = list(t)   # make a mutable copy
#     try:
#         for elem in s:
#             t.remove(elem)
#     except ValueError:
#         return False
#     return not t
    
# @pytest.mark.parametrize('pump_manfuacturer', ['HarvardApparatus', 
#                                                'Chemyx', 
#                                                'NewEra'])
# def test_Methods(pump_manufacturer):
#     """Test that Each Pump has the corrrect methods"""

#     methods = ['run', 'set_rate', 'stop', 'get_info', 'configure']
#     module_name = "pumps.{}".format(pump_manufacturer)
#     pump  = import_module(module_name)
#     pump_methods = []
#     #Check all attributes that are not protected 
#     # i.e. the don't start with __
#     for attr in dir(pump):
#         if attr.rstrip('__') == attr:
#             pump_methods.append(attr)
#     success = compare(pump_methods, methods)
#     assert success == True

# #Pull in list of all syringes manufacturers and models
# with open('syringes.json', 'r') as f:
#     syringe_data = json.load(f.read())


# @pytest.mark.parametrize('model',['PhD-Ultra'])
# @pytest.mark.parametrize('syringe_object', syringe_data['syringes'])
# def test_HarvardApparatus(model, syringe_object):
#     #Create serial port (#automatically imported form conftest)
#     ser = create_serial_port() 
    
#     #Construct syringe type dictionary
#     syringe_type = {'manufacturer': syringe_object['manufacturer'],
#                     'volume': syringe_object['volume']
#                     }

#     #Instantiate pump
#     pump =  PumpControl.HarvardApparatus(
#                                          model=model,
#                                          address=1,
#                                          syringe_type=syringe_type,
#                                          ser = ser)
    
#     #Construct volume
#     output = ser.readline()

    
    

       



  
