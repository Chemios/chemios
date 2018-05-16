'''
/*
 * Copyright 2018 Chemios
 * Chemios Reactor Brain Controller
 *
 * This code receives instructions from AWS IoT and used those to run the reactor.
 *
 */
 '''

import serial
import json
import time
import sys
from chemios.utils import serial_write, write_i2c, construct_cmd, sio_write
import re
import io
import logging


class Chemyx(object):
    """ Class for interacting with pumps

    Attributes:
        model (str): Pump model; either Chemyx,  NE-1000 or DIY
        address (str): Pump address
        diameter (float, optional): Diameter of syringe pump in millimeters. Defaults to 30 mm.
        volume (float, optional): Volume of syringe. Defaults to 10 mL
        rate_limits: array of lower limit and upper flowrate limit in microliters/hr
        ser (:obj:): Serial object from pyserial (used for Chemyx and NE-100 pump)
        bus (:obj:): i2C bus object if the DIY pump is used
    """

    def __init__(self, model, address, syringe_type={}, ser=None, bus=None):
        self.pump_models = {'names': ['NE-1000', 'DIY', 'Chemyx', 'HA-PHD-Ultra']}
        self.address = address #Adress for the pump
        self.model = model #model
        self.syringe_type = syringe_type
        self.ser = ser #serial object
        self.bus = bus #i2c bus object
        

        #Validation
        if self.model not in self.pump_models['names']:
            raise ValueError('Please choose one of the listed pumps'+ json.dumps(self.pump_models,indent=2))
        if self.model == 'NE-1000' and self.ser is None:
            raise ValueError('Serial object must be provided for communication with the NE-1000.')
        if self.model == 'DIY' and self.bus is None:
            raise ValueError('i2C bus must be provided for communication with the DIY pump.')
        if self.model == 'Chemyx' and self.ser is None:
            raise ValueError('Serial object must be provided for communication with the NE-1000.')
        if self.model == 'HA-PHD-Ultra' and self.ser is None:
            raise ValueError('Serial object must be provided for communication with Harvard Apparatus PHD Ultra')

        #Internal variables
        self.sio = io.TextIOWrapper(io.BufferedRWPair(self.ser, self.ser))
        self.rate = {'value': None,'units': None}
        self.direction = None #INF for infuse or WDR for withdraw
        self.sleep_time = 0.1
        try:
            #rate limits in microliters/hr
            self.rate_limits = self.syringe_type['rate_limits']
            self.diameter = self.syringe_type['diameter']
            #Volume in mL
            if self.syringe_type['volume'][1] != 'ml':
                raise ValueError("Volume must be in ml")
            self.volume = self.syringe_type['volume'][0]
        except KeyError:
            self.rate_limits = {}
            self.diameter = None
            self.volume =  None
            if self.model == 'Chemyx':
                raise ValueError("Please pass diameter, volume and rate limits array in syringe_type")
            else:
                pass

        #Set up pumps using serial
        if self.model == 'NE-1000':
            #Set NE-1000 continuous pumping (i.e., 0 volume to dispense)
            serial_write(self.ser, construct_cmd("VOL0\x0D", self.address), "setup continuous pumping")
            time.sleep(0.5)
            self.ser.flush()
        if self.model == 'Chemyx':
            #Check pump address by units (i.e., I'm setting pump_1 units to 1 and pump_2 units to 2)
            response = sio_write(self.sio, "view parameter\x0D", True, timeout =5)
            try:
                match2 = re.search(r'(?<=unit = )\d', response, re.M)
                unit_number = match2.group(0)
            except Exception:
                raise IOError("Wrong pump address")
            #raise IOError("Wrong pump address")
            if int(unit_number) != int(address):
                raise IOError("Wrong pump address")

            if self.diameter is not None:
                cmd = 'set diameter %0.3f\x0D'%(self.diameter)
                diameter = serial_write(self.ser, cmd, "set_diameter", True)
                self.ser.flush()
        #Set up PHD Ultra
        if self.model == 'HA-PHD-Ultra':    
            #Set the syringe type
            try:
                #Check that it's plugged into this port
                #and the right type of commands are being used
                # for i in range(3): self.ser.flush()
                # response = sio_write(self.sio, "CMD", True, timeout=5)
                # match = re.search(r'(Ultra)', response, re.M)
                # if match is None:
                #     status_text = "Pump not set to Ultra command set"
                #     raise IOError(status_text)
                cmd = "syrm {} {} {}\x0D".format(
                                             syringe_type["code"],
                                             syringe_type['volume'][0],
                                             syringe_type['volume'][1]
                )
                for i in range(3): self.ser.flush()
                sio_write(self.sio, cmd, False, timeout=1)
                time.sleep(0.1)
                #Check back on that the manfacturer was set correctly
                for i in range(3): self.ser.flush()
                output = sio_write(self.sio, "syrm\x0D", True, timeout = 2)
                logging.debug("Output from setting syringe manufacture: {}".format(output))
            except ValueError as e:
                logging.debug(e)


    def get_info(self):
        """ Get info about the current pump

        Yields:
            obj: model, address, syringe_diameter, rate

        Todo:
            * Properly implement reading information from serial
        """
        info = {'model': self.model,
                'address': self.address,
                'syringe_diameter': self.diameter,
                'rate': self.rate
                }
        if self.model == 'NE-1000':
            cmd = '%iPHN'%(self.address)
            output = serial_write(self.ser, cmd, 'get_info', True)
            info['phase'] = str(output)
            cmd = '%iVER'%(self.address)
            output2 = serial_write(self.ser, cmd, 'get_info', True)
            info['ver'] = output2
        if self.model == 'Chemyx':
            #Commenting out because of slow response time
            # response = sio_write(self.sio, "view parameter\x0D", True, timeout =5)
            # unit_table = {'0': 'MM', '1': 'UM', '2': 'MH','3':'UH'}
            # match1 = re.search(r'(?<=rate = )\d+', response, re.M)
            # value = match1.group()
            # match2 = re.search(r'(?<=unit = )\d', response, re.M)
            # unit_number = match2.group()
            # unit = unit_table[unit_number]
            # info['rate'] = {'value': value, 'units': unit }
            pass
        return info

    def run(self):
        """Run the pump with the internally stored settings
        Note:
            To run a pump, first call set_rate and then call run.
        """
        for i in range(5): self.ser.flush()
        if self.model == 'NE-1000':
            cmd = '%iRUN\x0D'%(self.address)
            serial_write(self.ser, cmd, 'run')
        if self.model == 'DIY':
            if self.direction == 'INF':
                cmd = "1:" + str(self.rate['value'])+ "&"
                print(cmd)
                write_i2c(cmd, self.bus, self.address)
            elif self.direction == 'WDR':
                cmd = "2:" + str(self.rate['value']) + "&"
                print(cmd)
                write_i2c(cmd, self.bus, self.address)
        if self.model == 'Chemyx':
            serial_write(self.ser, 'start\x0D', 'run')
        if self.model == 'HA-PHD-Ultra':
            serial_write(self.ser, 'irun\x0D', 'run')

    def set_diameter(self, diameter):
        """Set diameter of syringe on the pump
        Args:
            diameter (float): Syringe diameter in millimeters
        """
        if type(diameter) is not 'float':
            raise ValueError('Please enter a decimal value for the diameter.')
        self.diameter = diameter

        if self.model == 'NE-1000':
            cmd = '%iDIA%d\x0D'%(self.address, self.diameter) #set function to rate
            serial_write(self.ser, cmd, "set_diameter")
        if self.model == 'Chemyx':
            cmd = 'set diameter %d\x0D'%(self.diameter)
            serial_write(self.ser, cmd, "set_diameter" )
        if self.model == 'HA-PHD-Ultra':
            raise NotImplementedError("Use syringe_type to pass in syringe manufacturer and volume for Harvard Apparatus pumps")


    def set_rate(self, rate, direction):
        """Set the flowrate of the pump
        Note:
            To run a pump, first call set_rate and then call run.

        Args:
            rate (obj:'value', 'units'): {'value': pump flowrate, 'units': UM}
            direction (str): Direction of pump. INF for infuse or WDR for withdraw
        """
        #check that the direction is valid
        check = direction == "INF" or "WDR"
        if not check:
            raise ValueError('Must choose INF for infuse or WDR for withdraw')
   
        unit_conversion = {'MM': 60000, 'UM': 60 , "MH": 1000 , "UH": 1}
        #check that the units are one of the possible units
        try:
            unit_conversion[rate['units']]
        except KeyError:
            logging.warning("Please specify one of the following units\n'MM' (milliliters/min)\n'UM' (microliters/min)\n'MH' (milliliters/hour)\n'UH' (microliters/min)")
        
        # check that the rate is within the limits
        check_for_limits = len(list(self.rate_limits.keys())) > 0
        if check_for_limits:
            rate_value = rate['value']*unit_conversion[rate['units']] ## convert to microliters/hr
            if rate_value > self.rate_limits['max_rate']:
                logging.warning("Flowrate {} {} is greater than max rate limit".format(rate['value'],rate['units']))
                return
            if rate_value < self.rate_limits['min_rate']:
                logging.warning("Flowrate {} {} is less than minimum rate limit".format(rate['value'],rate['units']))
                return

        self.rate = rate
        self.direction = direction
        
        if self.model == 'NE-1000':
            # cmd = '%iFUN RAT\x0D'%self.address #set function to rate
            # serial_write(self.ser, cmd, "set_rate")
            self.ser.flush()
            time.sleep(0.1)
            cmd1 = '%iDIR%s\x0D'%(self.address, direction)
            serial_write(self.ser, cmd1, "set_rate") #Set the direction
            time.sleep(2)
            self.ser.flush()
            time.sleep(2)
            cmd2 = '%iRAT%.3f%s\x0D'%(self.address, rate['value'], rate['units'])
            serial_write(self.ser, cmd2, "set_rate") #Set the rate
        if self.model == 'Chemyx':
            #Using units as work-around for Chemyx pumps not having adresses
            #Address 0 corresponds with units 0, which is MM or milliliter/min
            #Address 1 corresponds with unit 1, which is UM or microliters/min
            if self.address == 0:
                #Convert to everything to mL/min for 
                unit_conversion = {'MM': 1, 'UM': 0.001 , "MH": 0.01667 , "UH": 0.00001667}
                conversion = unit_conversion[rate['units']]
                rate_value = conversion*self.rate['value']
                volume_converted = conversion*self.volume
            if self.address == 1:
                unit_conversion = {'MM': 1000, 'UM': 1, "MH": 16.667, "UH": 0.01667}
                conversion = unit_conversion[rate['units']]
                rate_value = conversion*self.rate['value']
                volume_converted = conversion*self.volume

            #Set rate
            self.ser.flush()
            cmd = 'set rate %0.3f\x0D'%(rate_value)
            print(cmd + " ml/min")
            serial_write(self.ser, cmd, "set_rate", True)
            time.sleep(0.1)
            #Set volume and direction
            if direction == 'INF':
                cmd = "set volume %0.3f\x0D"%(volume_converted)
            elif direction == 'WDR':
                cmd = "set volume %0.3f\x0D"%(-1*volume_converted)
            serial_write(self.ser, cmd, "set_rate", True)

            #Set units
            # unit_table = {'MM': 0, 'UM': 1, 'MH': 2, 'UH':3}
            # cmd = 'set units %i\x0D'%(unit_table[rate['units']])
            # serial_write(self.ser, cmd, "set_units", True)
            # time.sleep(0.1)
        if self.model == 'HA-PHD-Ultra':
            for i in range(5): self.ser.flush()
            unit_table = {'MM': 'ml/min', 'UM': 'ul/min' , "MH": 'ml/h' , "UH": 'ul/h'}
            units = unit_table[rate['units']]
            cmd = "irate {} {}\x0D".format(rate['value'], units)
            serial_write(self.ser, cmd, 'run')
            
    def stop(self):
        """Stop the pump"""
        if self.model == 'NE-1000':
            self.ser.flush()
            time.sleep(0.1)
            cmd = '%iSTP\x0D'%self.address
            serial_write(self.ser,cmd, "stop_pump")
            self.ser.flush()
        if self.model == 'Chemyx' or self.model == 'HA-PHD-Ultra':
            serial_write(self.ser, 'stop\x0D', "stop_pump")
        if self.model == 'DIY':
            my_cmd = "0:&"
            write_i2c(my_cmd, self.bus, self.address)

\