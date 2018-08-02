from abc import abstractmethod, ABC
from typing import List
from . import units

class Instrument(ABC):
    ''' Base class for instruments
    '''
    def __init__(self, type: str):
        self.type = type
        self.status = {'instrument_type': self.type}
        super().__init__()

    def __repr__(self):
        return '<Instrument: {}>'.format(self.type.replace('-',' ').replace('_', ' ').title())

    @abstractmethod
    def status(self):
        return self.status

_KWARGS = ['rate', 'volume', 'time']
_DIMENSIONS = ['[length]^3/[time]', '[length]^3', '[time]']

class SyringePump(Instrument):


    def __init__(self):
        self.type = 'syringe_pump'

    def status(self):
        '''Return an object with the status of the pump'''
        pass
        # status =  super().status()

        # #placedholders for gRPC method to get
        # #the status
        # pump_details = None

        # return status.update(pump_details)

    @staticmethod
    def _check_args(**my_args):
        ''' Check that  two of the necessary keyword args are specified
            and that the units are correct
        '''
        import pdb; pdb.set_trace()
        def check_units(value, dimension: str):
            if not value:
                return
            try:
                if value.check(dimension):
                    return
                else:
                    raise ValueError(f'Value: {value} must contain pint units of dimension {dimension}.')
            except KeyError:
                raise ValueError(f'Value: {value} must contain pint units of dimension {dimension}.')

        #Find the intersection of expected args and given args
        #and check that there are only two of the expected args
        #Then, check that the correct units are specified
        list_args = list(my_args.keys())
        if len(set(list_args).intersection(_KWARGS)) == 2:
              for index, arg in enumerate(_KWARGS):
                  value = my_args.get(arg, None)
                  check_units(value, _DIMENSIONS[index])
        else:
            raise ValueError('''Syringe Pump instructions must specify two of the
                             following three arguments: rate, volume or time.''')


    def infuse(self, **kwargs):
        ''' Infuse liquid from syringe 
        '''
        my_args = dict(kwargs)
        self._check_args(**my_args)
        passed_args = set(my_args).intersection(_KWARGS)
        
        #Send the passed args via grpc

    def withdraw(self, **kwargs):
        ''' Infuse liquid from syringe 
        '''
        self._check_args(kwargs)
        passed_args = set(args).intersection(_KWARGS)
        
        #Send the passed args via grpc
    
