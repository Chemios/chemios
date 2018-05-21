'''Tests for the SyringeData class.

These are tests for storing and retrieving data about syringes 
from the SyringeData json database. 
'''
import pytest
from chemios.components.pumps import SyringeData
from tinydb import Query
import os

filepath = 'test_syringe_data.json' 
@pytest.fixture()
def sdb():
    '''Fixture for setting up and tearing down a SyringeData database'''
    SyringeDB = SyringeData(filepath)
    yield SyringeDB
    #Delete Database on teardown
    os.unlink(filepath)

################ Test Syringe Methods #########################################

def test_syringe_id(sdb):
    '''Test if adding syringe id works correctly'''
    syringe_id = sdb.add_syringe(manufacturer ='Hamilton',
                                 volume=10, inner_diameter=14.74)
    assert syringe_id == 1

@pytest.mark.parametrize('manufacturer', ['Hamilton', 'HarvardApparatus'])
@pytest.mark.parametrize('volume', [0.001, 1, 10])
@pytest.mark.parametrize('inner_diameter', [14.474, 10])
def test_add_new_syringe(sdb, manufacturer, volume, inner_diameter):
    '''Test if adding a new unique syringe works properly'''
    sdb.add_syringe(manufacturer = manufacturer,
                    volume=volume, inner_diameter=inner_diameter)
    q = Query()
    result = sdb.syringes.search((q.manufacturer == manufacturer) &
                                 (q.volume == volume))
    expected_result = {
                        'manufacturer': manufacturer,
                        'volume': volume,
                        'inner_diameter': inner_diameter,
    }
    assert result[0] == expected_result

@pytest.mark.parametrize('manufacturer', ['Hamilton', 'GLE'])
@pytest.mark.parametrize('volume', [0.001, 1.0, 10.0])
@pytest.mark.parametrize('inner_diameter', [14.474, 10.0])
def test_update_syringe(sdb, manufacturer, volume, inner_diameter):
    '''Test if updating an existing syringe works properly'''
    syringe_id = sdb.add_syringe(manufacturer = manufacturer,
                                 volume=volume, inner_diameter=inner_diameter)
    #Update syringe
    syringe_id_update = sdb.add_syringe(manufacturer = manufacturer,
                                        volume=volume, 
                                        inner_diameter=inner_diameter+1.0)
    
    #Assert that the record was updated
    assert syringe_id == syringe_id_update

    #Assert that the corect information was updated
    q = Query()
    result = sdb.syringes.search((q.manufacturer == manufacturer) &
                                 (q.volume == volume))
    expected_result = {
                        'manufacturer': manufacturer,
                        'volume': volume,
                        'inner_diameter': inner_diameter+1.0,
    }
    assert result[0] == expected_result


@pytest.mark.parametrize('manufacturer', ['Hamilton', 'HarvardApparatus'])
@pytest.mark.parametrize('volume', [0.001, 1, 10])
@pytest.mark.parametrize('inner_diameter', [14.474, 10])
def test_find_syringe_id(sdb, manufacturer, volume, inner_diameter):
    '''Test if find_id works properly for syringes'''
    syringe_id = sdb.add_syringe(manufacturer = manufacturer,
                                 volume=volume, inner_diameter=inner_diameter)
    query = {
                        'manufacturer': manufacturer,
                        'volume': volume
    }
    query_id = sdb.find_id(query)
    assert syringe_id == query_id

################ Test Pump Methods #########################################
@pytest.mark.parametrize('manufacturer', ['HarvardApparatus'])
@pytest.mark.parametrize('model', ['Phd-Ultra'])
def test_add_new_pump(sdb, manufacturer, model):
    '''Test if adding a new unique pump works properly'''
    sdb.add_pump(manufacturer = manufacturer, model=model)
    q = Query()
    result = sdb.pumps.search((q.manufacturer == manufacturer) &
                              (q.model == model))
    expected_result = {
                        'manufacturer': manufacturer,
                        'model': model
    }
    assert result[0] == expected_result


@pytest.mark.parametrize('manufacturer', ['HarvardApparatus'])
@pytest.mark.parametrize('model', ['Phd-Ultra'])
def test_find_pump_id(sdb, manufacturer, model):
    '''Test if find_id works correctly for pumps'''
    pump_id = sdb.add_pump(manufacturer = manufacturer, model=model)
    query = {
                'manufacturer': manufacturer,
                'model': model
    }
    query_id = sdb.find_id(query)
    assert pump_id == query_id

@pytest.mark.parametrize('limits', [[10, 1000000],
                                    [0.0001, 100]])
def test_add_limits(sdb, limits):
    '''Test if adding limits works properly'''
    pump_id = sdb.add_pump(manufacturer = 'HarvardApparatus', 
                model='Phd-Ultra')
    syringe_id = sdb.add_syringe(manufacturer = 'Hamilton',
                    volume=10, inner_diameter=14.747)

    #Add limits
    sdb.add_limits(syringe_id=syringe_id, pump_id=pump_id,
                   min_rate=limits[0], max_rate=limits[1])

    #Check the pump object for correct limits
    pump = sdb.pumps.get(doc_id=pump_id)
    assert pump['limits'][str(syringe_id)] == limits


@pytest.mark.parametrize('limits', [[10, 1000000],
                                    [0.0001, 100]])
def test_find_limits(sdb, limits):
    ''' Test if find_limits method works properly'''
    syringe_id =  sdb.add_syringe(manufacturer = 'Hamilton',
                                  volume=10, inner_diameter=14.747)
    pump_id =  sdb.add_pump(manufacturer = 'HarvardApparatus', 
                            model='Phd-Ultra')

    #Add limits
    sdb.add_limits(syringe_id=syringe_id, pump_id=pump_id,
                   min_rate=limits[0], max_rate=limits[1])
    
    syringe_details = {
                        'manufacturer': 'Hamilton',
                        'volume': 10
    }

    pump_details = {
                        'manufacturer': 'HarvardApparatus',
                        'model': 'Phd-Ultra'
    }

    saved_limits = sdb.find_limits(syringe_details, pump_details)

    assert saved_limits == limits

    
    