import serial
import io
import re
from ._syringe_data import SyringeData
import os

def module_path():
    path = os.path.abspath(__file__)
    return os.path.dirname(path)

class Pump(object):
    '''Base class for pumps

    Attributes:
        name: Reference name for the pump (optional)
        model : Pump model  
        ser: The :class:`serial` object for the Chemyx pump
        units: Units to utilize

    '''
    def __init__(self, model:str, ser:serial.Serial, 
                 name:str = None, units:str = 'mL/min'):
        self.name = name
        self.model = model #model
        self.ser = ser #serial object
        self.units = units

        #Internal variables
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self.rate = {'value': None,'units': None}
        self.direction = None #INF for infuse or WDR for withdraw
        current_path = module_path()
        old_path = os.getcwd()
        os.chdir(current_path)
        self.sdb = SyringeData('../data/syringe_db.json')
        os.chdir(old_path)
        self.volume = None
        self.diameter = None
        self.units_dict = {'mL/min': '0', 'mL/hr': '1', 'uL/min': '2', 'uL/hr': 3}

    def _convert_volume(self, volume: dict):
        '''Convert volume to current units used by the pump
        Arguments:
            volume: Dictionary of value and units
        Returns:
            dict: Dictionary of value and units
        '''
        conversions = {'nL': 1e9, 'uL': 1e6, 'mL': 1e3, 'L': 1}
        units = self.units
        #Strip off time units
        units = units.strip('/hr')
        units = units.strip('/min')
        old_units =  volume['units'] 
        if old_units != units:
            #Convert units (go through liters)
            value = volume['value']/conversions[old_units]*conversions[units]
            volume = {'value': value, 'units': self.units}
        return volume

    def _convert_rate(self, rate: dict):
        '''Convet rate to current units used by pump
        Arguments:
            rate: Dictionary of 'value' of rate and 'units'
        Returns:
            dict: Dictionary of value and units of rate in current
                units used by the pump
        '''
        volume_conversions = {'nL': 1e9, 'uL': 1e6, 'mL': 1e3, 'L': 1}
        time_conversions = {'hr': 60, 'min': 1 }
        rate_value = rate['value']
        if rate['units'] != self.units:
            #Convert volume
            old_v_units = rate['units'].strip('/hr')
            old_v_units = old_v_units.strip('/min')
            v_units = self.units.strip('/hr')
            v_units = v_units.strip('/min')
            rate_value = rate_value/volume_conversions[v_units]*volume_conversions[v_units]
            
            #Convert time
            result = re.search(r'(?<=\/)(hr|min)', rate['units'], re.M)
            old_t_units= result[0]
            result = re.search(r'(?<=\/)(hr|min)', self.units, re.M)
            t_units = result[0]
            rate_value = rate_value/time_conversions[old_t_units]*time_conversions[t_units]
            return {'value': rate_value, 'units': self.units}
        else:
            return rate