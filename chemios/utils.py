'''
/*
 * Copyright 2018 Chemios
 * Chemios Reactor Brain Controller
 *
 * Useful Utilities
 *
 */
 '''

import numpy as np
import json
import logging
import datetime
import time
import sys
import glob
import serial
import datetime
import arrow

#Method for turning on and off the light source
def light_source(gpio, pin1, pin2, light_source_1_status, light_source_2_status):
    """Method for switching on light sources
    Note:
        Light Source 1 is for absorbance. Light Source 2 is for fluoresscence.
    """
    if light_source_1_status:
        gpio.output(pin1,gpio.HIGH)
        logging.debug("Light 1 for absorbance on")
    else:
        gpio.output(pin1,gpio.LOW)
        logging.debug("Light 1 for absorbance off")

    if light_source_2_status:
        gpio.output(pin2,gpio.HIGH)
        logging.debug("Light 1 for fluorescence on")
    else:
        gpio.output(pin2,gpio.LOW)
        logging.debug("Light 1 for fluorescence off")
    
#Convert data frame to list of lists
def convert_to_lists(df):
    output = []
    for i in range(len(list(df))):
        column = df.iloc[:,i]
        output.append(column.values.tolist())       
    for i in output:
        for j in i:
            try:
                x = output[i][j]                
                output[i][j] = x.item()
            except Exception:
                pass
    return output

#Import module
def import_module(name):
    '''Import a module from a string'''
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod 

# def make_json_compatible(data):
#     if isinstance(data, dict):
#         keys = list(data.keys())
#         for key in keys:
#             #Convert int64s to integers
#             print("here")
#             if isinstance(key, list):
#                 cmd = "data"
#                 for subkey in key:
#                     cmd = "{}['{}']".format(cmd, str(subkey))
#                 cmd = "value={}".format(cmd)
#                 exec(cmd)
#                 print("values{}".format(value))
#             else:
#                 value = data[key]
#             if isinstance(value, np.int64):
#                 data[key] = value.item()
#             if isinstance(value, list) or isinstance(value, np.ndarray):
#                 i = 0
#                 for x in value:
#                     if isinstance(x, np.int64):
#                          value[i]= data[key].item()
#                     i += 1
#                 print("list values {}".format(value))
#                 value = list(value)
#                 data[key] = value
#             if isinstance(value, dict):
#                 new_keys = list(value.keys())
#                 for new_key in new_keys:
#                     if isinstance(key, list):
#                         key.append(new_key)
#                     else:
#                         keys.append([key, new_key])
#     return data


def create_spectrum_update(run_uuid, step, stage_position, 
                           residence_time, absorbance_data, 
                           fluorescence_data):
    if absorbance_data is not None:
        wavelength = absorbance_data[0]
        absorbance_data = absorbance_data[1]
    if fluorescence_data is not None:
        fluorescence_data = fluorescence_data[1]
    update = {
             "time": datetime.datetime.now().isoformat(),
             "run_uuid": run_uuid,
             "procedure_step": step,
             "stage_position": int(stage_position),
             "residence_time": residence_time,
             "spectrum": {
                         "wavelength": wavelength,
                         "absorbance": absorbance_data,
                         "fluorescence": fluorescence_data
                        }
            }
    return update

#Useful function for serial
def serial_write(ser, cmd, handle, output=False):
    """ General Serial Writing Method

    Args:
        Ser (:object:): Serial object from pyserial
        cmd (str): String being sent
        handle(str): Function handle (needed for error reporting)
        output(bool): If true, fucntion returns output/errors from serial defvece
    """
    #ser.flushOutput()
    ser.write(cmd.encode())
    logging.debug('Sent serial cmd ' + cmd)
    response = ser.readline()
    #if output:
        #ser.flush()
        #callback = ser.readline()
        # if '?' in callback:
        #     print(cmd.strip()+' from ' + handle + ' not understood')
        # print("Callback)
        #print(callback)
        #return callback
    return response

def sio_write(sio, cmd, output=False, timeout = 5):
    """ General Serial Writing Method

    Args:
        sio (:object:): Serial object from pyserial
        cmd (str): String being sent
        output(bool): If true, function returns output/errors from serial device. Defaults to false.
        timeout (int): Tiemout in seconds. Defaults to 5 seconds. 
    Returns:
        Response from the serial buffer.
    """
    #Add carriage return at the end of the string if it was forgotten
    cmd = cmd + '\x0D'
    try:
        sio.write(cmd)
    except TypeError:
        try:
            sio.write(cmd.encode())
        except Exception:
            logging.warning("sio_write cannot send message: {}".format(cmd))
            return 1
    logging.debug('Sent serial cmd ' + cmd)
    if output:
        start = arrow.utcnow()
        timeout = datetime.timedelta(seconds = timeout)
        response_buffer = ''
        while True:
            sio.flush()
            time.sleep(0.1)
            response = sio.readline()
            check = response != 'Invalid Command!\n' or response != ''
            if check:
                response_buffer = str(response) + response_buffer
            else:
                return response_buffer
            elapsed_time = arrow.utcnow() - start
            if elapsed_time > timeout:
                logging.debug('chemiosbrain.utils.sio_write timeout after {} seconds.'.format(str(elapsed_time.seconds)))
                return response_buffer
    

#Construct command for NE-1000 pump
def construct_cmd(cmd, address):
    add = '%i'%address
    return add + cmd

def discover_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    #For windows
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    #for linux/cygwin
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')
    #for mac
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
        ports = ports + glob.glob('/dev/cu.usb*')
        print(ports)
    else:
        raise EnvironmentError('Unsupported platform')

    #Remove any ports that we don't want
    ports_to_remove = ['/dev/ttyS0', '/dev/ttyAMA0', '/dev/ttyprintk','/dev/tty.Bluetooth-Incoming-Port']
    for port in ports_to_remove:
        try:
            ports.remove(port)
        except Exception:
            pass

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

#i2C communicaiton function for i2C
def write_i2c(string, bus, address):
    """Method for writing to the DIY pump via i2c"""
    converted = []
    for b in string:
        #Convert string to bytes
        converted.append(ord(b))
    #Write converted string to given address with 0 offset
    bus.write_i2c_block_data(address,0, converted)
    return -1
