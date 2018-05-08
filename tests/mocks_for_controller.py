'''
/*
 * Copyright 2018 Chemios
 * Chemios Firmware
 *
 * Mock classes representing different serial devices. This is used for testing.
 *
 */
 '''
import time
import pandas as pd
from chemiosbrain.utils import convert_to_lists

#File paths
sample_spectrometer_data = './sample_data/sample_spectrometer_data.csv'

class MockPump(object):
    def __init__(self):
        self.diameter = None
        self.rate = {'value': 'null', 'units': 'null'}
        self.direction = None
        self.model = 'Chemyx'
        self.address = '1'
        self.direction = None
        self.status = 'stopped'

    def get_info(self):
        update = {
                  'rate' : self.rate,
                  'model': self.model,
                  'address': self.address,
                  'syringe_diameter': self.diameter,
                  'status': self.status
        }
        return update

    def run(self):
        self.status = 'running'
        return

    def set_diameter(self, syringe_diameter):
        self.diameter = syringe_diameter

    def set_rate(self, rate, direction):
        try:
            self.rate = rate
            self.direction = direction
        except KeyError:
            raise ValueError('Rate must be a dictionary with value and units')

    def stop(self):
        self.status = 'stopped'

class MockStage(object):
    def __init__(self):
        self.status = 'IDLE'

    def home(self):
        return "Moved"

    #TODO: Make this asynchronous
    def move_abs(self, position, blocking=True):
        self.status = 'BUSY'
        time.sleep(0.01)
        self.status = 'IDLE'

    def get_status(self):
        return self.status

    def stop(self):
        self.status = 'IDLE'
        return

class MockSpectrometer(object):
    def __init__(self):
        df = pd.read_csv(sample_spectrometer_data)
        self.data = convert_to_lists(df)

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass 

    def read_spectrometer_raw(self, integration_time):
        return self.data
    
    def store_blank(self, blank):
        pass
    
    def store_dark(self, dark):
        pass

    def absorbance_read(self, integration_time, scans_to_average, filter=0, normalized=False):
        return self.data

class MockTemperatureController(object):
    def __init__(self):
        self.setpoint = None
        self.temperature = None

    def set_temperature(self, temp_setpoint):
        self.setpoint = temp_setpoint
        self.temperature = temp_setpoint

    def get_current_temperature(self):
        update = {'temp_set_point': self.setpoint,
                  'current_temp': self.temperature}
        return update

class MockGpio(object):
    def HIGH(self):
        return "HIGH"

    def LOW(self):
        return "LOW"

    def output(self, pin, output):
        return
