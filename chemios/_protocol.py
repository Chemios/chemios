import queue
from abc import ABC, abstractmethod
from chemios.constants import StatusCodes

codes = StatusCodes()


class Protocol(ABC):
    '''Base class for protocols

    Note:
        Each protocol must implement the methods in protocol
    '''

    def __init__(self):
        self.state = {'status': codes.idle}
        self.readings_buffer = queue.Queue()

    @abstractmethod
    def status(self):
        '''Get the status of a protocol'''
        return self.state

    @abstractmethod
    async def start(self):
        '''Start a protocol'''
        pass

    async def _next_step(self):
        '''Internal method for continuing to the next step of a protocol'''
        pass

    def stop(self):
        '''Stop a protocol'''
        self.state['status'] = StatusCodes.stopped()

    def get_reading(self):
        '''Retrieve a reading from the readings buffer'''
        try:
            reading = self.readings_buffer.get(block=False)
            self.readings_buffer.task_done()
        except queue.Empty:
            reading = None
        return reading

    def clear_readings(self):
        '''Clear the readings buffer'''
        while not self.readings_buffer.empty():
            self.readings_buffer.get()
