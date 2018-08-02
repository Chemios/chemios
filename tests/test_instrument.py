from chemios.instruments import Instrument, SyringePump
from chemios import units
import pytest

@pytest.mark.parametrize('type',
                         [('syringe-pump', 'Syringe Pump'),
                          ('HPLC', 'Hplc'),
                          ('balance', 'Balance'),
                          ('liquid_handler', 'Liquid Handler')])
def test_instrument(type):
    ''' Test that instruments are represented correctly
    '''
    class ExampleInstrument(Instrument):
         def status(self):
             super().status()

    instr = ExampleInstrument(type[0])
    assert '<Instrument: {}>'.format(type[1]) == repr(instr)

@pytest.fixture
def sp():
    return SyringePump()

@pytest.mark.parametrize('rate', [100.0 * units.microliters/ units.minute])
@pytest.mark.parametrize('volume', [1.0 * units.milliliter])
def test_infuse(sp, rate, volume):
    sp.infuse(rate=rate, volume=volume)
