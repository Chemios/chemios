'''
/*
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
    
def convert_to_lists(df):
    '''Convert data frame to list of lists'''
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

def import_module(name):
    '''Import a module from a string'''
    components = name.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod 


#Useful functions for serial
def serial_write(ser, cmd):
    """ General Serial Writing Method

    Args:
        Ser (:object:): Serial object from pyserial
        cmd (str): String being sent
        handle(str): Function handle (needed for error reporting)
        output(bool): If true, fucntion returns output/errors from serial defvece
    """
    ser.flushOutput()
    ser.write(cmd.encode())
    logging.debug('Sent serial cmd ' + cmd)

def sio_write(sio, cmd, 
              output=False, exp = None, ctx = 'Device', 
              timeout = 2):
    """ General Serial Writing Method with reading response

    Args:
        sio (:object:): io.Wrapper object from pyserial
        cmd (str): String being sent
        exp (str): Expected response (optional)
        ctx (str): The device being communicated with. Used for debug messages (optional)
        output(bool): If true, function returns output/errors from serial device. Defaults to false.
        timeout (int): Timeout in seconds. Defaults to 2 seconds. 
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
            response = response.strip('\n')
            response = response.strip('\r')
            if response != '':
                response_buffer = str(response) + response_buffer
            else:
                if response != exp and exp:
                    logging.warning('Did not receive expected response of {} from command {}. '
                                    '{} might not be connected.'
                                    .format(exp, cmd, ctx))
                return response_buffer
            elapsed_time = arrow.utcnow() - start
            if elapsed_time > timeout:
                logging.debug('chemios.utils.sio_write timeout after {} seconds.'.format(str(elapsed_time.seconds)))
                if response != exp and exp:
                    logging.warning('Did not receive expected response of {} from command {}. '
                                    '{} might not be connected.'
                                    .format(exp, cmd, ctx))
                return response_buffer
        

class SerialTestClass(object):
    """A serial port test class using a mock port """
    def __init__(self):
        self._port = "loop://"
        self._timeout = 0
        self._baudrate = 9600
        self.ser = \
            serial.serial_for_url(url=self._port,
                                  timeout=self._timeout,
                                  baudrate=self._baudrate)

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

def write_i2c(string, bus, address):
    """Method for writing via i2c"""
    converted = []
    for b in string:
        #Convert string to bytes
        converted.append(ord(b))
    #Write converted string to given address with 0 offset
    bus.write_i2c_block_data(address,0, converted)
    return -1
