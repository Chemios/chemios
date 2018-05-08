'''
/*
 * Copyright 2018 Chemios
 * Chemios Firmware
 *
 * Tests of the chemios Reactor and FlowReactor classes.
 *
 */
 '''
from chemiosbrain.controller import Reactor, FlowReactor
from mocks_for_controller import MockPump, MockStage, MockSpectrometer, MockTemperatureController, MockGpio
import json
import unittest
import uuid
from datetime import timedelta
import arrow
import threading

#Paths to sample data files
instruction_file_json = 'sample_data/sample_instruction.json'
procedure_file_json = 'sample_data/sample_procedure.json'
sample_blank_file_csv = 'sample_data/sample_blank_data.csv'
sample_dark_file_csv = 'sample_data/sample_dark_data.csv'
sample_stage_positions_file_csv = 'sample_data/sample_stage_positions.csv'

class GeneralReactorSetup(unittest.TestCase):
    def setUp(self):
        self.id = hex(uuid.getnode())
        self.ip = '192.168.1.1'
        self.react = Reactor(self.id,self.ip)
        with open(instruction_file_json) as json_data:
            self.sample_instruction = json.load(json_data)
        with open(procedure_file_json) as json_data:
            self.sample_procedure = json.load(json_data)

    def tearDown(self):
        del self.react

#Test general reactor initialization methods
class TestInitializationMethods(GeneralReactorSetup):
    #Create new instruction
    def test_new_instruction(self):
        response = self.react.new_instruction(self.sample_instruction)
        self.assertEqual(response, "Single Instruction Created")

    #Check status of new instruction
    def test_instruction_status(self):
        self.react.new_instruction(self.sample_instruction)
        status = self.react.get_status()
        self.assertEqual(status['status'], "running single instruction")
        #Check if update is within the last second
        self.assertEqual(status['total_steps'], 1)
        #Check that procedure status updates are cleared.
        #Put lambda in front to make sure error loaded before function runs
        self.assertEqual(status['run_uuid'], None)
        self.assertEqual(status['procedure_step'], 0)
        self.assertEqual(status['steps_remaining'], 1)
        self.assertEqual(status['total_steps'], 1)

    #Create New Procedure
    def test_new_procedure(self):
        response = self.react.new_instruction(self.sample_procedure)
        self.assertEqual(response, "Procedure Created")

    #Check status of a procedure
    def test_procedure_status(self):
        self.react.new_instruction(self.sample_procedure)
        status = self.react.get_status()
        self.assertEqual(status['status'], 'running procedure')
        self.assertEqual(status['run_uuid'], 'aad9c46c-34db-4d9e-91c6-2fdc1af07c69')
        #Check if update is within the last second
        self.assertEqual(status['procedure_step'], 0)
        self.assertEqual(status['steps_remaining'], 2)
        self.assertEqual(status['total_steps'], 2)

#Test general reactor methods for incrmementing through instruction or procedure
class TestIncrementMethods(GeneralReactorSetup):
    def test_next_step_instruction_status(self):
        self.react.new_instruction(self.sample_instruction)
        response = self.react.next()
        self.assertEqual(response, "Single Instruction Initiated")
        status = self.react.get_status()
        self.assertEqual(status['status'], 'running single instruction')
        self.assertEqual(status['procedure_step'], 1)
        self.assertEqual(status['steps_remaining'], 0)
        self.assertEqual(status['total_steps'], 1)

        response = self.react.next()
        self.assertEqual(response, "Instruction running")
        status = self.react.get_status()
        self.assertEqual(status['status'], 'running single instruction')
        self.assertEqual(status['run_uuid'], None)
        self.assertEqual(status['procedure_step'], 1)
        self.assertEqual(status['total_steps'], 1)
        self.assertEqual(status['steps_remaining'], 0)


    #Check if step returns the proper status
    def test_next_step_procedure_status(self):
        self.react.new_instruction(self.sample_procedure)
        response = self.react.next()
        self.assertEqual(response, "Next Step Initiated")
        status = self.react.get_status()
        self.assertEqual(status['status'], 'running procedure')
        self.assertEqual(status['procedure_step'], 1)
        self.assertEqual(status['steps_remaining'], 1)
        self.assertEqual(status['total_steps'], 2)

        response = self.react.next()
        self.assertEqual(response, "Next Step Initiated")
        status = self.react.get_status()
        self.assertEqual(status['status'], 'running procedure')
        self.assertEqual(status['procedure_step'], 2)
        self.assertEqual(status['steps_remaining'], 0)
        self.assertEqual(status['total_steps'], 2)

        response = self.react.next()
        self.assertEqual(response, "Run Complete")
        status = self.react.get_status()
        self.assertEqual(status['status'], 'stopped')
        self.assertEqual(status['run_uuid'],'aad9c46c-34db-4d9e-91c6-2fdc1af07c69')
        self.assertRaises(KeyError, lambda: status['total_steps'])
        self.assertRaises(KeyError, lambda: status['steps_remaining'])

    def test_stop(self):
        self.react.new_instruction(self.sample_procedure)
        stop = self.react.stop()
        status = self.react.get_status()
        self.assertEqual(status['status'], 'stopped')
        self.assertEqual(status['run_uuid'],'aad9c46c-34db-4d9e-91c6-2fdc1af07c69')
        self.assertEqual(status['procedure_step'], 0)

#General setup and tear down for tests for the flow_reactor class
class GeneralFlowReactor(unittest.TestCase):
    def setUp(self):
        self.id = hex(uuid.getnode())
        self.ip = '192.168.1.1'
        self.flow_reactor = FlowReactor(uuid = self.id, ip_address = self.ip,
                                        pump_1 = MockPump(), pump_2 = MockPump(), gas = MockPump(),
                                        tube_diameter = 1.59, total_tube_length = 30,
                                        stage=MockStage(), spectrometer = MockSpectrometer(),
                                        temperature_controller = MockTemperatureController(),
                                        gpio_interface= MockGpio(), light_source_1_pin=18, light_source_2_pin=13)
        with open(instruction_file_json) as json_data:
            self.sample_instruction = json.load(json_data)
        with open(procedure_file_json) as json_data:
            self.sample_procedure = json.load(json_data)

    def tearDown(self):
        del self.flow_reactor

#Tests instantion and creation of instruction and procedure
class TestInitializationFlowReactor(GeneralFlowReactor):
    #Create new instruction
    def test_new_instruction(self):
        response = self.flow_reactor.new_instruction(self.sample_instruction)
        self.assertEqual(response, "Single Instruction Created")

    #Create New Procedure
    def test_new_procedure(self):
        response = self.flow_reactor.new_instruction(self.sample_procedure)
        self.assertEqual(response, "Procedure Created")

    #Test reading in blank and dark data
    def test_read_blank_and_dark(self):
        self.flow_reactor.read_blank_and_dark(sample_blank_file_csv, sample_dark_file_csv)

    #Test reading in stage positions
    def test_read_stage_positions(self):
        self.flow_reactor.read_stage_positions(sample_stage_positions_file_csv)

#Test main instruction
class TestInstructionMethodFlowReactor(GeneralFlowReactor):
    def setUp(self):
        super(TestInstructionMethodFlowReactor, self).setUp()
        self.flow_reactor.read_blank_and_dark(sample_blank_file_csv, sample_dark_file_csv)
        self.flow_reactor.read_stage_positions(sample_stage_positions_file_csv)

    #Check status of new instruction
    def test_instruction_status(self):
        self.flow_reactor.new_instruction(self.sample_instruction)
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], "running single instruction")
        self.assertEqual(status['total_steps'], 1)
        #Check that procedure status updates are cleared.
        self.assertEqual(status['run_uuid'], None)
        self.assertEqual(status['procedure_step'], 0)
        self.assertEqual(status['steps_remaining'], 1)
        self.assertEqual(status['total_steps'], 1)

    #Check status of a procedure
    def test_procedure_status(self):
        self.flow_reactor.new_instruction(self.sample_procedure)
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], 'running procedure')
        self.assertEqual(status['run_uuid'], 'aad9c46c-34db-4d9e-91c6-2fdc1af07c69')
        self.assertEqual(status['procedure_step'], 0)
        self.assertEqual(status['steps_remaining'], 2)
        self.assertEqual(status['total_steps'], 2)

class TestIncrementMethodFlowReactor(GeneralFlowReactor):
    def setUp(self):
        super(TestIncrementMethodFlowReactor, self).setUp()
        self.flow_reactor.read_blank_and_dark(sample_blank_file_csv, sample_dark_file_csv)
        self.flow_reactor.read_stage_positions(sample_stage_positions_file_csv)
        self.e = threading.Event()

    def test_next_step_instruction_status(self):
        self.flow_reactor.new_instruction(self.sample_instruction)
        response = self.flow_reactor.next(self.e)
        self.assertEqual(response, "Single Instruction Initiated")
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], 'running single instruction')
        self.assertEqual(status['procedure_step'], 1)
        self.assertEqual(status['steps_remaining'], 0)
        self.assertEqual(status['total_steps'], 1)
        self.assertEqual(status['pump_1_rate'], 120.1)
        self.assertEqual(status['pump_2_rate'], 60)
        self.assertEqual(status['pump_3_rate'], 4.25)
        self.assertEqual(status['temp_set_point'], 90)
        self.assertTrue(status['light_source_1_on'])
        self.assertFalse(status['light_source_2_on'])
        self.assertEqual(status['uv_spec_integration_time'], 3000)
        self.assertEqual(status['uv_spec_scans_to_average'], 12)
        self.assertEqual(status['viewing_port'], 2)
        self.e.clear()

        response = self.flow_reactor.next(self.e)
        self.assertEqual(response, "Instruction running")
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], 'running single instruction')
        self.assertEqual(status['run_uuid'], None)
        self.assertEqual(status['procedure_step'], 1)

    #Test calling next step in a procedure
    def test_next_step_procedure_status(self):
        self.flow_reactor.new_instruction(self.sample_procedure)
        response = self.flow_reactor.next(self.e)
        self.assertEqual(response, "Next Step Initiated")
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], 'running procedure')
        self.assertEqual(status['procedure_step'], 1)
        self.assertEqual(status['steps_remaining'], 1)
        self.assertEqual(status['total_steps'], 2)
        self.assertEqual(status['pump_1_rate'], 6.25) #Calculated these manually
        self.assertEqual(status['pump_2_rate'], 2.08)
        self.assertEqual(status['pump_3_rate'], 4.17)
        self.assertEqual(status['temp_set_point'], 90)
        self.assertFalse(status['light_source_1_on'])
        self.assertFalse(status['light_source_2_on'])
        self.assertEqual(status['uv_spec_integration_time'], 3000)
        self.assertEqual(status['uv_spec_scans_to_average'], 10)
        self.assertEqual(status['viewing_port'], 3)

        response = self.flow_reactor.next(self.e)
        self.assertEqual(response, "Next Step Initiated")
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], 'running procedure')
        self.assertEqual(status['procedure_step'], 2)
        self.assertEqual(status['steps_remaining'], 0)
        self.assertEqual(status['total_steps'], 2)
        self.assertEqual(status['pump_1_rate'], 6.25) #Calculated these manually
        self.assertEqual(status['pump_2_rate'], 2.08)
        self.assertEqual(status['pump_3_rate'], 4.17)
        self.assertEqual(status['temp_set_point'], 100)
        self.assertFalse(status['light_source_1_on'])
        self.assertFalse(status['light_source_2_on'])
        self.assertEqual(status['uv_spec_integration_time'], 3000)
        self.assertEqual(status['uv_spec_scans_to_average'], 10)
        self.assertEqual(status['viewing_port'], 3)
        self.e.clear()
        response = self.flow_reactor.next(self.e)
        self.assertEqual(response, "Run Complete")
        status = self.flow_reactor.get_status()
        self.assertEqual(status['status'], 'idle')
        self.assertEqual(status['run_uuid'],None)
        self.assertEqual(status['procedure_step'], None)
        self.assertRaises(KeyError, lambda: status['total_steps'])
        self.assertRaises(KeyError, lambda: status['steps_remaining'])



if __name__ == "__main__":
    unittest.main()
