'''Chemyx Pump Module

Chemyx manufacturers several types of syringe pumps, which can be found on their website:
https://www.chemyx.com/

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

class Chemyx(Pump):
    """ Class for interacting with Chemyx syringe pumps

    Note:
        The available models are the Fusion 100, Fusion 200, Fusion 4000, 
        Fusion 6000, Nanojet and OEM.

        *Baudrates*:
        9600 only: Fusion 4000, Fusion 6000
        38400 only: Nanojet, OEM
        9600 or 38400: Fusion 100, Fusion 200


        See https://www.chemyx.com/support/knowledge-base/programming-and-computer-control/getting-started/ for more information

    Attributes:
        model : Pump model, currently only OEM  
        ser: The :class:`serial` object for the Chemyx pump
        **name: Reference name for the pump. Defaults to mL/min.
        **units: Units to utilize. Defaults to ChemyxPump.
        **syringe_manufacturer: Syringe manufacturer
        **syringe_volume: Syringe volume in mL
        **retry: seconds to sepnd retrying reading serial data back
    """

    def __init__(self, model:str, ser:serial.Serial, **kwargs):
        self.name = kwargs.get('name', 'ChemyxPump')
        self.units = kwargs.get('units', 'mL/min')
        self.retry = kwargs.get('retry', 1)
        super(Chemyx, self).__init__(model=model, ser=ser, name=self.name, units=self.units)

        #Validation------------------------------------------------------------
        #Check that the model is one of the available models
        models = ['Fusion 100', 'Fusion 200', 'Fusion 4000', 'Fusion 6000', 'NanoJet', 'OEM']
        if self.model not in models:
            raise ValueError('{} is not one of the currently available pump models'.format(self.model))

        #Check for the correct baudrate
        if self.model in ['OEM', 'Nanoject'] and self.ser.baudrate != 38400:
            raise ValueError("Baudrate is {}. Please change serial baudrate to 38400 for Chemyx {}."
                             .format(self.ser.baudrate, self.model))
        if self.model in ['Fusion 4000', 'Fusion 6000'] and self.ser.baudrate != 9600:
            raise ValueError("Baudrate is {}. Please change to 9600 for Chemyx {}."
                             .format(self.ser.baudrate, self.model))
        check = int(self.ser.baudrate) == 9600 or int(self.ser.baudrate) == 38400
        if self.model in ['Fusion 100', 'Fusion 200'] and not check:
            raise ValueError("Baudrate is {}. Please change to 9600 or 38400 for Chemyx {}."
                             .format(self.ser.baudrate, self.model))        
        
        #Connection------------------------------------------------------------
        logging.debug("Connecting to Chemyx pump")
        #Set units
        self.set_units(self.units)
        #Set syringe if available
        self.syringe_manufacturer  = kwargs.get('syringe_manufacturer', None)
        self.volume  = kwargs.get('syringe_volume', None)
        if self.syringe_manufacturer and self.volume:
            self.set_syringe(manufacturer=self.syringe_manufacturer,
                             volume=self.volume)


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
        try:
            response = sio_write(self.sio, "view parameter\x0D", True, timeout=self.retry)
            #Invert key, value mapping on units dict
            unit_table ={v: k for k, v in self.units_dict.items()}
            #Get rate
            match1 = re.search(r'(?<=rate = )\d+.(\d+)?', response, re.M)
            value = match1.group()
            match2 = re.search(r'(?<=unit = )\d', response, re.M)
            unit_number = match2[0]
            unit = unit_table[unit_number]
            info['rate'] = {'value': value, 'units': unit }
        except Exception as e:
            logging.warning(e)
        return info

    def run(self):
        """Run the pump with the internally stored settings
        Note:
            To run a pump, first call set_rate and then call run.
        """
        self.ser.flushOutput()
        serial_write(self.ser, 'start\x0D')

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
        elif not self.diameter:
            raise ValueError("{} {}mL syringe not in the database. "
                             " To use a custom syringe, pass inner_diameter."
                             .format(manufacturer, volume))

        #Send command and check response
        cmd = 'set diameter %0.3f\x0D'%(self.diameter)
        expected_response = 'diameter = %0.3f\x0D'%(self.diameter) 
        sio_write(self.sio, cmd,
                  output = True, exp=expected_response, ctx = self.name, 
                  timeout=self.retry)
        
        #Change internal variables
        volume = self._convert_volume({'value': volume, 'units': 'mL'})
        self.volume = volume
        
    def set_units(self, units: str):
        '''Set the pump units
        Arguments:
            units: One of the unit strings in the note
        Note:
            Possible units are: mL/min, mL/hr, uL/min, uL/hr
            Calling this function will also update the internal
            rate and volume to match the new untis
        '''
        #validation
        try:
            unit_number = self.units_dict[units]
        except KeyError:
            raise ValueError("Invalid unit: {}."
                                "Please specify one of the following units: mL/min, mL/hr, uL/min, uL/hr"
                                .format(units))
        #Set units
        cmd = "set units {}".format(unit_number)
        expected_response = "units = {}".format(unit_number)
        sio_write(self.sio, cmd,
                    output = True, exp=expected_response, ctx = self.name, 
                    timeout=self.retry)
        #Update internal variable
        self.units = units
        if self.volume:
            self.volume =self._convert_volume(self.volume)
            self.rate = self._convert_rate(self.rate)
        return self.units

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
        #Check if syringe volume has been set
        if not self.volume:
            raise ValueError("Please set the syringe before calling set_rate.")

        #Convert units if necessary
        if rate['units'] != self.units:
            rate = self._convert_rate(rate)
        
        #Set rate
        self.ser.flushOutput()
        cmd = 'set rate %0.3f\x0D'%(rate['value'])
        expected_response = 'rate = %0.3f\x0D'%(rate['value'])
        sio_write(self.sio, cmd,
                  output = True, exp=expected_response, ctx = self.name, 
                  timeout=self.retry)
        time.sleep(0.1)
        
        #Set direction using the volume
        if direction:
            if direction == 'INF':
                cmd = "set volume %0.3f\x0D"%(self.volume['value'])
            elif direction == 'WDR':
                cmd = "set volume %0.3f\x0D"%(-1*self.volume['value'])
            else:
                raise ValueError('Must choose INF for infuse or WDR for withdraw')
            
            serial_write(self.ser, cmd)

        #Change internal variable
        self.rate = rate
            
    def stop(self):
        """Stop the pump"""
        serial_write(self.ser, 'stop\x0D')
    