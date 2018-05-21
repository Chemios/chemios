'''SyringeData class for storing the rate limits of syringes

Each syringe pump and syringe combination can achieve a minimum
and maximum flowrate. These min/max rates are a function of 
the diameter of the syringe and the precision/power of the pump. 
This database is designed to cache those min/max limits, so the
pump classes can validate whether a given flowrate can be achieved 
by a syringe pump. 

'''
from tinydb import TinyDB, Query
import logging

def update_dict(key, value):
    '''Method to update a nested dictionary in a tinydb table'''
    def transform(doc):
        try: 
            if type(doc[key]) == dict:
                doc[key] = doc[key].update(value)
        except KeyError:
            doc.update({key: value})
        except AttributeError:
            doc[key] = value
    return transform


class SyringeData(object):
    '''Class for storing syringe data
    Attributes:
        filepath: Path to the database file
    Notes:
        The database file will opened if it already exists.
        Otherwise a new file will be created.
    '''

    def __init__(self, filepath: str):
        #Create or open a syringe_data database 
        self.db = TinyDB(filepath)
        self.syringes = self.db.table('syringes')
        self.pumps = self.db.table('pumps')

    def add_syringe(self, manufacturer: str, 
                    volume: float, inner_diameter: float):
        '''Add a syringe to the syringe_data database
        Arguments:
            manufacturer: Syringe manufacturer
            volume: Syringe volume in mL
            inner_diameter: Syringe Inner Diameter in mm
        Returns:
            int: unique id of the database entry
        Note:
            This method will update an entry that is an exact match
            for manufacturer and volume.  Otherwise, it will create 
            a new entry.
        '''
        new_syringe = {
                        'manufacturer': manufacturer,
                        'volume': volume,
                        'inner_diameter': inner_diameter,
        }
        #Add or update syringe information
        Syringe = Query()
        syringe_id = self.syringes.upsert(new_syringe,
                                          (Syringe.manufacturer == manufacturer) &
                                          (Syringe.volume == volume))         
        logging.debug('{} {} mL syringe added to the database.\n'
                      .format(manufacturer, volume))
        if type(syringe_id) == list:
            syringe_id = syringe_id[0]
        return syringe_id

    def add_pump(self, manufacturer: str, model: str):
        '''Add a pump to the syringe_data database

        Arguments:
            manufacturer: Pump manufacturer
            model: Pump model
        Returns:
            int: unique id of the table entry
        '''
        new_pump = {
                    'manufacturer': manufacturer,
                    'model': model
        }

        #Check that same pump does not exist
        try:
            pump_id = self.find_id(new_pump)
        except ValueError:
            # If the pump doesn't exist, it will throw a ValueError
            pump_id = None

        if pump_id is not None:
            raise ValueError('{} {} already exists in the database'
                            .format(manufacturer, model))
                            
        #Add pump information
        pump_id = self.pumps.insert(new_pump)
        logging.debug('{} {} pump added to the database.\n'
                      .format(manufacturer, model))
        if type(pump_id) == list:
            pump_id = pump_id[0]
        return pump_id

    def add_limits(self, pump_id: int, syringe_id: int, 
                   min_rate: float, max_rate: float):
        '''Add min and max rates for pump and syringe combination
        Arguments: 
            pump_id: Unique id of the pump
            syringe_id: Unique id of the syringe
            min_rate: Minimimum flowrate in microliters/min
            max_rate Maximum flowrate in microliters/min
        '''
        #First check that the syringe type exists
        if not self.syringes.contains(doc_ids=[syringe_id]):
            raise ValueError("Unique syringe id {} does not exist in the database."
                            .format(syringe_id))

        new_limits = [min_rate, max_rate]
        pump = self.pumps.get(doc_id=pump_id)
        try:
            pump['limits'][str(syringe_id)] = new_limits
        except KeyError:
            pump['limits'] = {str(syringe_id): new_limits}
        except TypeError:
            pump['limits'] = {str(syringe_id): new_limits}
        except AttributeError:
            pump['limits'] = {str(syringe_id): new_limits}
            
        #Add or update the pump table
        self.pumps.update(pump,doc_ids=[pump_id])
    
    def find_id(self, query: dict):
        '''Search for a syringe or pump unique id
        Arguments:
            query: A dictionary containing the syringe manufacturer and volume 
                or the pump manufacturer and model:
        Example:
            Searching for a syringe::
            ```python
            sdb = SyringeData('example.json')
            query = {'manufacturer': 'Hamilton', 'volume': 10}
            id = sdb.get_id(query)
            print(id)
            ```
        Returns:
            int: Unique id of the syringe or pump

            This will return none if no pump or syringe is found
        Raises:
            ValueError
        '''
        #Validation
        keys = list(query.keys())
        if 'manufacturer' not in keys:
            raise ValueError('Must pass manufacturer in query object')

        #Get unique id
        if 'volume' in keys:
            Syringes = Query()
            syringe = self.syringes.search((Syringes.manufacturer == query['manufacturer']) &
                                           (Syringes.volume == query['volume']))
            if len(syringe) > 1:
                raise LookupError('There are multiple matches for this'
                                  ' syringe manufacturer and volume: {}.'.format(syringe))
            if len(syringe) == 0:
                return None
            return syringe[0].doc_id
        elif 'model' in keys:
            Pumps = Query()
            pump = self.pumps.get((Pumps.manufacturer == query['manufacturer']) &
                                  (Pumps.model == query['model']))
        
            if not pump:
                raise ValueError('{} {} pump is not in database'
                                 .format(query['manufacturer'], query['model']))

            return pump.doc_id
    
    def find_limits(self, syringe_details, pump_details):
        '''Find the maximum and minimum rate for a given pump and syringe combination
        Arguments:
            syringe_details: A dictionary containing the syringe manufacturer and volume
            pump_details: A dictionary containing the pump manufacturer and model
        Returns:
            list: The zeroth index is min rate is the first index max rate.
            Both rates are in microliters/min
        '''
        syringe_id = self.find_id(syringe_details)
        pump_id = self.find_id(pump_details)
        pump = self.pumps.get(doc_id=pump_id)
        limits = pump['limits'][str(syringe_id)]
        return limits


        



