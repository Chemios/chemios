from ._chemyx import Chemyx
from ._harvard_apparatus import HarvardApparatus
from ._new_era import NewEra
from typing import NamedTuple

 
#Create syringe_type tuple for valdiation
class _syringe(NamedTuple):
    manufacturer: str
    volume: float

get_syringe_data()