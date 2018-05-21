'''Harvard Apparatus Pump Module

Harvard Apparatus manufacturers several types of pumps

This module can be used to control Chemyx pumps.

'''

import serial 
import time
import re
import io
import logging
from chemios.utils import serial_write, write_i2c, sio_write
from ._syringe_data import SyringeData
from ._base import Pump

class HarvardApparatus(Pump):
    """ Class for interacting with Haravard Apparatus syringe pumps
    Attributes:
        name: Reference name for the pump (optional)
        model : Pump model
        ser: The :class:`serial` object for the Chemyx pump
        units: Units to utilize

    Note:
        Available models: Phd-Ultra
    """

    def __init__(self, model:str, ser:serial.Serial, 
                name = 'HarvardApparatus', units = 'mL/min'):
        self.name = name
        self.model = model #model
        self.ser = ser #serial object
        self.units = units

        #Internal variables
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self.rate = {'value': None,'units': None}
        self.direction = None #INF for infuse or WDR for withdraw
        self.sdb = SyringeData('../../../data/syringe_db.json')
        self.volume = None
        self.diameter = None
        self.units_dict = {'mL/min': '0', 'mL/hr': '1', 'uL/min': '2', 'uL/hr': 3}
        self.timeout = 1

        #Validation------------------------------------------------------------
        #Check that the model is one of the available models
        models = ['Phd-Ultra']
        if self.model not in models:
            raise ValueError('{} is not one of the currently available pump models'.format(self.model))     
        
        #Connection------------------------------------------------------------
        logging.debug("Connecting to {} pump".format(self.name))
        #Check that it's plugged into this port
        #and the right type of commands are being used
        response = sio_write(self.sio, "CMD\x0D", True, timeout=1)
        if self.model == 'Phd-Ultra':
            match = re.search(r'(Ultra)', response, re.M)
            if match is None:
                status_text = "Pump not set to Ultra command set"
                raise IOError(status_text)
   

    def get_info(self):
        """ Get info about the current pump

        Yields:
            obj: model, address, syringe_diameter, rate
        """
        info = {
                'name': self.name,
                'model': self.model,
                'syringe_diameter': self.diameter,
                'rate': self.rate
                }
        return info

    def run(self):
        """Run the pump with the internally stored settings
        Note:
            To run a pump, first call set_rate and then call run.
        """
        self.ser.flushOutput()
        serial_write(self.ser, 'irun\x0D')

    def set_syringe(self, manufacturer:str, volume: float,
                    inner_diameter:float=None):
        """Set diameter of syringe on the pump
        Args:
            manufacturer: Syringe manufacturer
            volume: Syringe total volume in mL
            inner_diameter: Inner diameter of the syringe in mm (optional)                   
        """
        #Try to get syringe diameter from database
        self.diameter = self.sdb.find_diameter(manufacturer=manufacturer,
                                               volume=volume)
        if not self.diameter and inner_diameter:
           self.diameter = inner_diameter
        else:
            raise ValueError("{} {} syringe not in the database. "
                             " To use a custom syringe, pass inner_diameter."
                             .format(manufacturer, volume))

        #Send command and check response
        cmd = 'syrm Custom %0.3f\x0D'%(self.diameter)
        expected_response = 'syrm Custom %0.3f\x0D'%(self.diameter) 
        sio_write(self.sio, cmd,
                  output = True, exp=expected_response, ctx = self.name, 
                  timeout=self.timeout)
        
        #Change internal variables
        volume = self._convert_volume({'value': volume, 'units': 'mL'})
        self.volume = volume

    def set_rate(self, rate, direction=None):
        """Set the flowrate of the pump
        Note:
            To run a pump, first call set_rate and then call run.
            See :meth:`chemios.components.pumps.Chemyx.set_rate`for
            units format.

        Args:
            rate (obj:'value', 'units'): {'value': pump flowrate, 'units': UM}
            direction (str): Direction of pump. INF for infuse or WDR for withdraw (optional)
        Note:
            The only way to set direction on Chemyx pumps is by changing the volume.
            Currently, the software resets the volume to the max volume of the syringe.

        """ 
        #Convert units if necessary
        if rate['units'] != self.units:
            rate = self._convert_rate(rate)
        
        #Set rate
        self.ser.flushOutput()
        unit_table = {'mL/min': 'ml/min', 'uL/min': 'ul/min' , "mL/hr": 'ml/h' , "uL/hr": 'ul/h'}
        units = unit_table[rate['units']]
        cmd = "irate {} {}\x0D".format(rate['value'], units)
        serial_write(self.ser, cmd)

        #Change internal variable
        self.rate = rate
            
    def stop(self):
        """Stop the pump"""
        serial_write(self.ser, 'stop\x0D')