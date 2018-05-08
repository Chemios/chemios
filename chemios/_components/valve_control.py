import json
import time
import sys
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)
# set the pin to #22 on the raspberry pi which GPIO25
GPIO.setup(25, GPIO.OUT)
# set the pin to #18 on the raspberry pi which GPIO24
GPIO.setup(24, GPIO.OUT)


class valve(object):
    """ Class for interacting with valves

    Attributes:
        model (str): valve model; probably outlet
    """

    def __init__(self, model):
        self.valve_models = {'names': ['outlet']}
        self.model = model  # model

        # Validation
        if self.model not in self.valve_models['names']:
            raise ValueError('Please choose one of the listed valves' +
                             json.dumps(self.valve_models, indent=2))
        

        # Internal variables
        self.status = True
        self.sleep_time = 0.1

    def get_info(self):
        """ Get info about the current valve

        Yields:
            obj: model
        """
        info = {'model': self.model}
        return info

    def get_status(self):
        """ Get status of the current valve

        Yields:
            open or closed as boolean, false for closed
        """
        return self.status

    def switch(self):
        """Run the valve with the internally stored settings
        Note:
            To run a valve, first call set_rate and then call run.
        """
        if self.model == 'outlet':
            self.status = not self.status
            if GPIO.input(25):
                GPIO.output(25, GPIO.HIGH)
            else:
                GPIO.output(25, GPIO.LOW)

    def stop(self):
        """Stop the valve"""
        if self.model == 'outlet':
            self.status = not self.status
            if GPIO.input(24):
                GPIO.output(24, GPIO.HIGH)
            else:
                GPIO.output(24, GPIO.LOW)
