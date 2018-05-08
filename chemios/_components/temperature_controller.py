'''
/*
 * Copyright 2018 Chemios
 * Chemios Temperature Cotnrol
 *
 * This code controls an Omega CN 9311 Temperature Controllers
 *
 */
 '''

import minimalmodbus

#required values
pre_security_check = 5
pre_security_clear_post = 6
security_check = 0
#minimal modbus
#function codes
output_status = 1
input_status = 2
read_register = 3
force_coil = 5
write_register = 6
device_info = 16

#memory registers ######DO NOT MODIFY############
temperature_register = 28 #read only
temperature_setpoint_register = 127 # read/write

output_register = None    ## currently unknown TODO find output register
device_info_register = 0x04FC #read only ## type of instrument and output configuration
input_register = 0x04
pre_security_register = 768
security_register_pre = 5376
security_register_post = 5632

class TemperatureController(object):
    '''Class to Control Omega CN 9311 Temperature Controller
    Attributes
        port (str): Serial port over which communication should be sent
        slave_address (int): Address of the temperature controller from 1 to 247
    Notes:
        Set the address on the Level C of the menu of the omega temperature controller
    '''
    
    def __init__(self, port, slave_address):
        self.controller = minimalmodbus.Instrument(port, slave_address, mode=minimalmodbus.MODE_RTU)
        #Try a command to see if the instrument works
        self.controller.read_register(temperature_setpoint_register, numberOfDecimals=1 )

    def get_current_temperature(self):
        ''' Method to get the current temperature
        Yields
            update = {
                    'temp_set_point': setpoint in deg C,
                    'current_temp': temperature in deg C
                    }
        '''
        setpoint = self.controller.read_register(temperature_setpoint_register, numberOfDecimals=1 ) #read only one setpoint register
        temperature = self.controller.read_register(temperature_register, 1)
        update = {
                  'temp_set_point': setpoint,
                  'current_temp': temperature
                 }
        return update

    def set_temperature(self, temp_set_point): #memory location for temperature set needed
        ''' Method to set the temperature
        Args:
            temp_set_point (float): temperature setpoint in deg C
        '''
        #TODO ensure that the proper responses are received
        #Enter Program Mode
        self.controller.write_register(pre_security_register,pre_security_check, functioncode = write_register)
        self.controller.write_register(security_register_pre, security_check)
        #write to setpoint register
        self.controller.write_register(temperature_setpoint_register, temp_set_point, numberOfDecimals = 1, functioncode = write_register)
        #exit Program Mode
        self.controller.write_register(pre_security_register, pre_security_clear_post)
        self.controller.write_register(security_register_post, security_check)
        #Get setpoint and current temperature
        update = self.get_current_temperature()
        return update



