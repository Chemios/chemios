from chemios import Protocol
from random import randint, random
import asyncio
from time import sleep


class MockProtocol(Protocol):
    '''MockProtocol for testing'''

    def status(self):
        '''Get the status of a protocol'''
        return self.state

    async def start(self):
        '''Start a protocol'''
        self._steps = randint(1, 5)
        continuing = True
        while continuing:
            await asyncio.sleep(0)
            continuing = self._next_step()

    def _next_step(self):
        '''Internal method for continuing to the next step of a protocol'''
        sleep(random()*5)
        data = {
                'test_1': randint(1, 10),
                'test_2': randint(10, 20)
        }
        self.readings_buffer.put(data, block=True, timeout=3)
        self._step = self._step + 1
        if self._step > self._steps:
            return False
        else:
            return True


