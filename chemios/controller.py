"""
/*
 * Copyright 2018 Chemios
 * Chemios Firmware
 *
 * Reactor and FlowReactor classes.  Used to directly control the reactor
 *
 */
 """
from .utils import light_source, convert_to_lists, create_spectrum_update
import datetime
import time
import arrow
from csv import writer
from math import pi
from decimal import Decimal
import pandas as pd
import logging
import threading
import numpy as np
import serial

#set up status codes. DO NOT CHANGE THESE.
status_codes = ['offline', #0
                'starting', #1
                'running single instruction', #2
                'running procedure', #3
                'stopped', #4
                'idle', #5
                'error'] #6

#Room temperaeture in deg C
room_temp = 25

# Blank data fileName
blank_filename = "blank.csv"

#stage length (in microsteps)
stage_length = 200

class Reactor(object):
    """Class for abstraction of reactors
    Args:
        uuid(str): the uuid of the reactor
        ip_address(str): the ip address of the reactor
    """
    def __init__(self, uuid, ip_address):
        self.uuid = uuid
        self.ip_address = ip_address
        self.status_code = status_codes[5] #init with idle status
        self.single_instruction = None
        self.procedure = None
        self.step = None
        self.total_steps = None
        self.run_uuid = None
        self.lock_step = threading.Lock() #lock for modifying state of procedure

    def get_status(self):
        """General method for getting status of a reactor
        Yields:
            output(obj): Object with status update
        """
        with self.lock_step:
            status_update= {
                            'status': self.status_code,
                            'uuid': self.uuid,
                            'run_uuid': self.run_uuid,
                            'procedure_step': self.step
                            }
            #If running single instruction or procedure, update steps
            if self.status_code == status_codes[3] or self.status_code == status_codes[2]:
                steps = {'total_steps': self.total_steps,
                        'steps_remaining': self.total_steps - self.step
                        }
                status_update.update(steps)
        return status_update

    def new_instruction(self,instruction):
        """General method for creating a new procedure
        Args:
            instruction(dict): A dictionary received from AWS IoT (see sample_procedure.json for an example)
        """
        #Check formatting of instruction
        if 'type' not in list(instruction.keys()):
            logging.warning('Instruction not formatted correctly')

        #Stop the reactor immediately if called
        if instruction['type'] == "stop":
            with self.lock_step:
                self.status_code = status_codes[4]
            logging.debug("Stopping reactor")
            return 1         

        #Check to make sure a procedure is not already running
        if self.status_code == status_codes[3]:
            logging.warning("Procedure already running")
            return 1

        if instruction['type'] == "single instruction":
            self.procedure = None
            self.instruction = instruction['instruction']
            self.status_code = status_codes[2]
            self.total_steps = 1
            self.step = 0
            self.run_uuid = None
            return_text = "Single Instruction Created"
            logging.debug(return_text)
        elif instruction['type'] == "procedure":
            self.single_instruction = None
            self.status_code = status_codes[3]
            self.procedure = instruction['procedure']
            self.run_uuid = self.procedure['run_uuid']
            self.step = 0
            self.total_steps = len(instruction['procedure']['steps'])
            return_text = "Procedure Created"
            logging.debug(return_text)
        return return_text

    def next(self):
        """General method for running the next step
        Note:
             This will take care of the end of the procedure/instruction
             Add an override method (pre-filter) for each reactor to handle how to go between steps.
        """
        status_text = "No procedure loaded"
        #Acquire lock to prevent simultaneous updates
        with self.lock_step:
            #If already running single instruction or at the end of a procedure...
            if self.status_code == status_codes[2] or self.status_code == status_codes[3]:
                if self.total_steps - self.step == 0:
                    if self.status_code == status_codes[2]:
                        status_text = ("Instruction running")
                    #Stop reactor if at end of a procedure
                    if self.status_code == status_codes[3]:
                        status_text =("Run Complete")
                        # set to stopped
                        self.status_code = status_codes[4]
                #Move to next step of procedure
                elif self.status_code == status_codes[3] and self.step <= self.total_steps:
                    self.step = self.step + 1
                    status_text = "Next Step Initiated"
                elif self.status_code == status_codes[2]:
                    self.step = self.step + 1
                    status_text = "Single Instruction Initiated"
                logging.debug(status_text)
        return status_text

    def stop(self):
        """General method for stopping a procedure
        Note:
            Add an override method (pre-filter) for each reactor to handle stopping.
        """
        #Acquire lock to prevent simultaneous updates/reads
        with self.lock_step:
            self.status_code = status_codes[4]

    def update_ip(self, ip_address):
        """Method for updating the ip address"""
        self.ip_address = ip_address

    def update_uuid(self, uuid):
        """Method for updating reactor uuid"""
        self.uuid = uuid

class FlowReactor(Reactor):
    """Class for the flow reactor
    Args:
        uuid(str): the uuid of the reactor
        ip_address(str): the ip address of the reactor
        pump_1(obj): Pump object as instance pump_control class
        pump_2(obj): Pump object as instance pump_control class
        gas(obj):Pump or mass flow controller object
        tube_diameter(float): Tube diameter in mm
        total_tube_length(float): The length of the reactor tubing including preheater in cm
        stage(obj): Zaber serial AsciiAxis object (https://www.zaber.com/support/docs/api/core-python/0.8.1/ascii.html#asciicommand)
        spectrometer(obj): Instance of the seabreeze object
        GPIO(obj): Raspberry Pi GPIO
        light_source_1_pin(int): The number of the GPIO pin used for the light source 1
        light_source_2_pin(int): The number of the GPIO pin used for the light source 2
    Notes:
        * Lock_1 is used for the stage, Lock_2 is used for spectrum_buffer
    """
    def __init__(self, uuid, ip_address,
                pump_1, pump_2, gas,
                tube_diameter, total_tube_length,
                stage, spectrometer,
                temperature_controller,
                gpio_interface, light_source_1_pin, light_source_2_pin):
        super(FlowReactor, self).__init__(uuid, ip_address)
        self.pump_1 = pump_1
        self.pump_2 = pump_2
        self.gas = gas
        self.tube_diameter = tube_diameter
        self.total_tube_length = total_tube_length
        self.stage = stage
        self.spectrometer = spectrometer
        self.temperature_controller = temperature_controller
        self.gpio_interface  = gpio_interface
        self.light_source_1_pin = light_source_1_pin
        self.light_source_2_pin = light_source_2_pin
        self.light_source_status = {'light_source_1_on': False, 'light_source_2_on': False}
        self.uv_spec_settings = {'integration_time': 1000, 'scans_to_average': 10}
        self.stage_positions = None
        self.current_stage_position = None
        self.viewing_port_number = None
        self.spectrum_buffer = []

        #Create a dictionary of locks
        device_lock_names = ['pump_1', 'pump_2', 'gas', 'stage', 'gpio', 'spectrum_buffer', 'temperature_controller']
        self.device_locks = {}
        for lock_name in device_lock_names:
            self.device_locks[lock_name] = threading.Lock()

    def read_blank_and_dark(self, blank_file, dark_file):
        """Read in absorbance blank data from file
        Args:
            blank_file(str): relative path to blank csv
            dark_file(str): relative path to dark csv
        """
        with self.spectrometer as spec:
            data = pd.read_csv(blank_file)
            blank = convert_to_lists(data)
            spec.store_blank(blank)
            data = pd.read_csv(dark_file)
            dark = convert_to_lists(data)
            spec.store_dark(dark)
            logging.info('Blank and dark saved')
 
    def read_stage_positions(self, stage_positions_file):
        """Read in stage positions for holes from file
        Args:
            file(str): relative path to file with stage positions
        """
        data = pd.read_csv(stage_positions_file)
        with self.lock_step:  
            self.stage_positions = list(data.stage_positions)
        logging.debug('Stage positions saved')

    def get_status(self):
        """Get the current status of the reactor

        Todo:
            * Make calls to pump and stage asynchronous
            * Convert all flowrates to microliters/min(UM) if they are not
        """
        #Call the general method to handle status codes etc.
        status_update = super(FlowReactor, self).get_status()

        #Get the current temperature
        with self.device_locks['temperature_controller']:
            try:
                temperature = self.temperature_controller.get_current_temperature()
            except ValueError:
                logging.warning("Temperature Controller not working")
            except OSError:
                logging.warning("Temperature Controller not working")
            except IOError:
                logging.warning("Temperature Controller not working")

        #Get pump_1 update
        with self.device_locks['pump_1']:
            try:
                pump_1_status = self.pump_1.get_info()
                pump_1_status = pump_1_status['rate']['value']
            except serial.SerialException:
                logging.warning("Cannot communicate with pump_1")

        #Get pump_2 update
        with self.device_locks['pump_2']:
            try:
                pump_2_status = self.pump_2.get_info()
                pump_2_status = pump_2_status['rate']['value']
            except serial.SerialException:
                logging.warning("Cannot communicate with pump_2")

        #Get pump_3 update
        with self.device_locks['gas']:
            try:
                pump_3_status = self.gas.get_info()
                pump_3_status = pump_3_status['rate']['value']
            except serial.SerialException:
                logging.warning("Cannot communicate with pump_3")

        with self.lock_step:
            try:
                FlowReactor_update = {
                                        'pump_1_rate': pump_1_status,
                                        'pump_2_rate': pump_2_status,
                                        'pump_3_rate': pump_3_status,
                                        'temp_set_point': temperature['temp_set_point'],
                                        'light_source_1_on': self.light_source_status['light_source_1_on'],
                                        'light_source_2_on': self.light_source_status['light_source_2_on'],
                                        'uv_spec_integration_time': self.uv_spec_settings['integration_time'],
                                        'uv_spec_scans_to_average': self.uv_spec_settings['scans_to_average'],
                                        'stage_position': self.current_stage_position,
                                        'viewing_port': self.viewing_port_number
                                        }
                status_update.update(FlowReactor_update)
            except KeyError:
                logging.warning("KeyError in FlowReactor_update")
        return status_update

    def new_instruction(self, instruction, override=False):
        '''Method to create a new instruction
        Note:
            Inherits the parent class method and clears spectrum_buffer.
        Args:
            instruction(dict): A dictionary received from AWS IoT (see tests/sample_data/sample_procedure.json for an example)
            override (bool): If true, will clear the spectrum bufffer if there are spectra remaining. Defaults to False (recommended).
        """
        '''
        status_text = super(FlowReactor, self).new_instruction(instruction)

        with self.device_locks['spectrum_buffer']:     
            if len(self.spectrum_buffer) >= 1 and not override:
                logging.warning('The spectrum buffer has spectra remaining')
                return 1
            logging.debug("Resetting the spectrum buffer")
            self.spectrum_buffer = []
        
        if instruction['type'] == "store blank":
            self.store_blank(1, 10)

        logging.debug(status_text)
        return status_text

    def next(self,e):
        '''Method to call the next step of a procedure or single instruction
        Args:
            e (:obj:): A threading object that is false by default. Set to true at the end of the step
        '''
        #Verify that stage positions are available
        if len(self.stage_positions) < 1:
            raise NameError("Please load stage positions using the read_stage_positions method for calling next")

        #Call the general method to handle status codes, steps etc.
        status_text = super(FlowReactor, self).next()

        #Shutdown behavior after a procedure (not a single instruction)
        if self.status_code == status_codes[4]:
            self.stop()        

        # #Pass if already running single instruction
        # if self.status_code == status_codes[2] and self.step == 1:
        #     logging.debug(status_text)
        #     return status_text

        #Run single instruction
        if self.status_code == status_codes[2]:
            #Set temperature
            with self.device_locks['temperature_controller']:
                self.temperature_controller.set_temperature(self.instruction['temp_set_point'])
            #Update Pumps
            with self.lock_step:
                pump_1_rate = self.instruction['pump_1_rate']
                pump_2_rate = self.instruction['pump_2_rate']
                gas_rate = self.instruction['pump_3_rate']

            rate_1 = {'value': pump_1_rate, 'units': 'UM'}
            rate_2 = {'value': pump_2_rate, 'units': 'UM'}
            rate_3 = {'value': gas_rate, 'units': 'UM'}
            with self.device_locks['pump_1']:
                self.pump_1.set_rate(rate_1, 'INF')

            with self.device_locks['pump_2']:
                self.pump_2.set_rate(rate_2, 'INF')
                
            with self.device_locks['gas']:
                self.gas.set_rate(rate_3, 'INF')
            
            time.sleep(2)
                    #TODO: Run these asynchronously
            with self.device_locks['pump_1']:
                self.pump_1.run()

            with self.device_locks['pump_2']:
                self.pump_2.run()
                
            with self.device_locks['gas']:
                self.gas.run()

            #Update Stage
            self.viewing_port_number = self.instruction['viewing_port']
            try:
                self.current_stage_position = self.stage_positions[self.viewing_port_number-1]
            except IndexError:
                logging.warning("Stage position outside available positions. Going to maximum position")
                self.current_stage_position = max(self.stage_positions)

            self.device_locks['stage'].acquire()
            try:
                self.stage.stop() #Stop the stage if it's moving
                self.stage.move_abs(self.current_stage_position, True)
            except ValueError:
                logging.debug("Cannot move stage")
            finally:
                self.device_locks['stage'].release()

            #Update Light Source and Spectrum
            light_source(self.gpio_interface,
                    self.light_source_1_pin,
                    self.light_source_2_pin,
                    self.instruction['light_source_1_on'],
                    self.instruction['light_source_2_on'])
            with self.lock_step: 
                self.light_source_status = {'light_source_1_on': self.instruction['light_source_1_on'],
                                        'light_source_2_on': self.instruction['light_source_2_on']}                      
                self.uv_spec_settings = {'integration_time': self.instruction['uv_spec_integration_time'],
                                        'scans_to_average': self.instruction['uv_spec_scans_to_average']}
            with self.spectrometer as spec:
                spectrum  = spec.absorbance_read(integration_time =self.uv_spec_settings['integration_time'], 
                                                 scans_to_average = self.uv_spec_settings['scans_to_average'],
                                                 filter = 300, normalized = False)

            #residence_time = 0.25*pi*(self.tube_diameter/10)**2*self.total_tube_length/total_rate*1000*60                                            
            update = create_spectrum_update(run_uuid= self.run_uuid, step= self.step, 
                                            stage_position = self.current_stage_position, residence_time = 'Not implemented', 
                                            absorbance_data = spectrum , fluorescence_data = None)                                             
            with self.device_locks['spectrum_buffer']:
                self.spectrum_buffer.append(update)
            e.set()
            return status_text

        #Run a procedure
        if self.status_code == status_codes[3]:
            #Convert to flow rate (all rates in microliters/min)
            with self.lock_step:
                step = self.procedure['steps'][self.step-1]
            precursor_ratio = step['precursor_ratio']
            gas_to_liquid_ratio = step['gas_liquid_ratio']
            total_rate = step['net_flow_rate']
            rate_1 = Decimal(precursor_ratio*total_rate/(precursor_ratio+1)/(gas_to_liquid_ratio+1))
            rate_2 = Decimal(total_rate/(precursor_ratio+1)/(gas_to_liquid_ratio+1))
            rate_3 = Decimal(gas_to_liquid_ratio/(gas_to_liquid_ratio+1)*total_rate)
                
            ###Round and convert to float
            rate_1 = float(round(rate_1, 2))
            rate_2 = float(round(rate_2, 2))
            rate_3 = float(round(rate_3, 2))

            #Run the step
            ###Heat reactor to desired temp
            with self.device_locks['temperature_controller']:
                try:
                    self.temperature_controller.set_temperature(step['temp_set_point'])
                except ValueError:
                    logging.warning("Temperature Controller not working")
                except OSError:
                    logging.warning("Temperature Controller not working")
                except IOError:
                    logging.warning("Temperature Controller not working")

            ###Start pumps flowing
            ####TODO: Choose lower flowrate for equilibration
            rate_1 = {'value': rate_1, 'units': 'UM'}
            rate_2 = {'value': rate_2, 'units': 'UM'}
            rate_3 = {'value': rate_3, 'units': 'UM'}
            with self.device_locks['pump_1'], self.device_locks['pump_2'], self.device_locks['gas']:
                self.pump_1.set_rate(rate_1, 'INF')
                self.pump_2.set_rate(rate_2, 'INF')
                self.gas.set_rate(rate_3, 'INF')
                #In theory, the pumps should just update automagically if they are already running
                if self.step == 1:
                    self.pump_1.run()
                    self.pump_2.run()
                    self.gas.run()

            ###Move stage home if not already
            self.device_locks['stage'].acquire()
            try:
                self.stage.home()
            except ValueError:
                logging.debug("Cannot home stage")
            finally:
                self.device_locks['stage'].release()   

            ###Sleep for 3 residence times
            ####TODO: figure out a reasonable time to sleep
            # residence_time = 0.25*pi*(self.tube_diameter/10)**2*self.total_tube_length/total_rate*1000*60
            # sleep_time = 3*residence_time
            # logging.info("Sleeping for 3 residence times: " + str(sleep_time) + " seconds") 
            # time.sleep(sleep_time)
            ###Move Stage to required postions and take measurments
            sleep_time = 30
            logging.info("sleeping for {} seconds".format(sleep_time))
            time.sleep(sleep_time)
            done = False
            while not done:
                #check if temperature w/in 2 deg C of setpoint
                with self.device_locks['temperature_controller']:
                    try:
                        current_temperature = self.temperature_controller.get_current_temperature()
                    except ValueError:
                        logging.warning("Temperature Controller not working")
                    except OSError:
                        logging.warning("Temperature Controller not working")
                    except IOError:
                        logging.warning("Temperature Controller not working")

                check = abs(current_temperature['current_temp']-step['temp_set_point']) <= 2.0

                i=1
                if check:
                    for position in self.stage_positions:
                        #TODO: Call stage in a non-blocking manner
                        self.device_locks['stage'].acquire()
                        try:
                            self.stage.move_abs(position, True)
                        except ValueError:
                            logging.debug("Cannot move stage")
                        finally:
                            self.device_locks['stage'].release()  
                        
                        with self.lock_step:
                            self.current_stage_position = position
                            self.viewing_port_number = i
                        i = i + 1

                        #Take Absorbance Measurement
                        if step['absorbance']:
                            #Update light source
                            light_source(self.gpio_interface,
                                         self.light_source_1_pin,
                                         self.light_source_2_pin,
                                         True, False)
                            with self.lock_step:
                                self.light_source_status = {'light_source_1_on': True,
                                                            'light_source_2_on': False}
                                #UV Spec Setting
                                self.uv_spec_settings = {'integration_time': step['integration_time'],
                                                         'scans_to_average': 10}
                            #Use with statement to prevent issues with spectrometer locking out
                            with self.spectrometer as spec:
                                absorbance_spectrum  = spec.absorbance_read(integration_time =self.uv_spec_settings['integration_time'], 
                                                                 scans_to_average = self.uv_spec_settings['scans_to_average'],
                                                                 filter = 300, normalized = False)
                                                 
                        #Take Fluorescence Measurement
                        if step['fluorescence']:
                            #TODO: Implement fluorescence reading
                            hello  = 1

                        #Turn off light sources before moving to next stage position                  
                        light_source(self.gpio_interface,
                                     self.light_source_1_pin,
                                     self.light_source_2_pin,
                                     False, False)
                        with self.lock_step:
                            self.light_source_status = {'light_source_1_on': False,
                                                        'light_source_2_on': False}
                        #residence_time = 0.25*pi*(self.tube_diameter/10)**2*self.total_tube_length/total_rate*1000*60                                            
                        update = create_spectrum_update(run_uuid= self.run_uuid, step= self.step, 
                                                        stage_position = self.current_stage_position, residence_time = 'Not implemented', 
                                                        absorbance_data = absorbance_spectrum , fluorescence_data = None)                                             
                        self.spectrum_buffer.append(update)
                    done = True
        #Set the thread flag to true
        e.set()
        return status_text

    def get_spectrum(self, blocking=True, timeout=10, no_logging=True):
        ''' Method to get spectra from the spectrum_buffer
        Note:
            This will get only the first spectra in buffer.  So, multiple calls are needed if there are more spectra.
        Args:
            blocking (bool): Defaults true, which blocks and wait for spectra. If false, tries to return spectra immediately.
            timeout (int): Timeout in seconds. Defaults to 10 seconds.
        '''
        start_time = arrow.utcnow()
        timeout = datetime.timedelta(seconds = timeout)
        if not blocking:
            self.device_locks['spectrum_buffer'].acquire()
            try:
                #Pop the first spectrum in the buffer
                spectrum = self.spectrum_buffer.pop(0)
                return spectrum
            except IndexError:
                if not no_logging:
                    logging.debug('chemiosbrain.controller.get_spectrum has no spectra to return')
                return 1
            finally:
                self.device_locks['spectrum_buffer'].release()

        #Blocking code
        while True:
            #check if there are spectra in the buffer
            if len(self.spectrum_buffer) >=1:
                self.device_locks['spectrum_buffer'].acquire()
                try:
                    #Pop the first spectrum in the buffer
                    spectrum = self.spectrum_buffer.pop(0)
                    return spectrum
                except IndexError:
                    pass
                finally:
                    self.device_locks['spectrum_buffer'].release
            elapsed_time = arrow.utcnow() - start_time
            if elapsed_time > timeout:
                status_text = 'chemiosbrain.controller.get_spectrum timeout after {} seconds.'.format(str(elapsed_time.seconds))
                logging.debug(status_text)
                return 1

    def store_blank(self, number_of_turnovers, port_number):
        """Method to collect a blank
        Notes: 
            Flows at the max flowrate to clear the system, then collects blank.  
        Args:
            number_of_turnovers (int): Number of times the system must be cleared
            port_number (int): The port number at which to measure
        """
        #Check to make sure a procedure is not already running
        if self.status_code == status_codes[3]:
            return_text = "Procedure already running"
            logging.warning(return_text)
            return 1
        #Check inputs
        if not isinstance(number_of_turnovers, int): raise ValueError("number_of_turnovers must be an integer")
        if not isinstance(port_number, int): raise ValueError("port_number must be an integer")
        # Diameter in mm, length in cm
        # Converted cm to mm then calculated volume in mm^3 which is equivalent to microliters
        reactor_volume = (self.total_tube_length / 10) * pi * (self.tube_diameter ** 2) / 4

        # maximum flow rate of the Hamilton 10mL syringe used, in microliters / hour
        max_syringe_flow_rate = 1880770

        # time to empty the reactor in minutes, converted from hours
        time_to_empty = reactor_volume / max_syringe_flow_rate * 60

        #make the rates for pumps
        rate_1 = {'value': max_syringe_flow_rate, 'units': 'UM'}
        rate_2 = {'value': max_syringe_flow_rate, 'units': 'UM'}
        
        #set the pumps to the predfined rates
        self.pump_1.set_rate(rate_1, 'INF')
        self.pump_2.set_rate(rate_2, 'INF')
        
        #Update Stage
        self.viewing_port_number = port_number  # go to the specified port number
        self.device_locks['stage'].acquire()
        try:
            self.stage.stop() # Stop the stage if it's moving
            self.stage.move_abs(self.current_stage_position, True)
        except ValueError:
            logging.debug("Cannot move stage")
        finally:
            self.device_locks['stage'].release()  
        # updates position of stage in program
        self.current_stage_position = self.stage_positions[self.viewing_port_number]
           

        # gets the start and end time
        start_time = time.time()
        end_time = time.time()

        #while loop runs for the time until it empties times the number of turnovers specified
        while end_time - start_time < time_to_empty * number_of_turnovers:
            #runs the pumps
            self.pump_1.run()
            self.pump_2.run()

            #TODO these two need an integration time
            with self.spectrometer as spec:
                 spectrum = spec.read_spectrometer_raw()
            wavelengths = spectrum[0]
            intensities = spectrum[1]

            #updates the end time 
            end_time = time.time()

            #should write all data to csv file defined at top of file, has append file extension
            with open(blank_filename, 'a') as csvfile:
                #initializes the writing object
                writeOut = writer(csvfile)
                #makes the title line
                writeOut.writerow(['wavelength'] + ['intensity'])
                #iterates through data indices in wavelengths
                for i in range(0, len(wavelengths)):
                    #error check just in case intensities is shorter than wavelengths
                    if len(intensities) < i:
                        #prints to csv file
                        writeOut.writerow([wavelengths[i], intensities[i]])
        return
    
    def save_stage_positions(self, threshold):
        ''' Finds the positions of the holes on the reactor
        '''
        raise NotImplementedError()
        self.stage.home()
        position = 0
        while position < stage_length: 
            spectrum_buffer = []
            self.stage.move_rel(0.1*stage_length)
            hit_threshold = False
            while not hit_threshold:
                with self.spectrometer as spec:
                    spectrum = spec.read_spectrometer_raw()
                spectrum_buffer.append(spectrum)
                averaged = np.average(spectrum_buffer, axis=0)
                maximum = np.amax(averaged)
                if maximum >= threshold:
                    self.stage.stop()
                    self.stage.move_rel(-0.01*stage_length)
                    self.get_status()
         
    def stop(self):
        '''Stops the pumps, cools the reactor to room temperature and homes the stage.
        '''
        super(FlowReactor, self).stop()
        #Stop reagent flow
        with self.device_locks['pump_1']:
            self.pump_1.stop()
        with self.device_locks['pump_2']:
            self.pump_2.stop()
        with self.device_locks['gas']:
            self.gas.stop()
            
        #Cool down reactor to room temp
        with self.device_locks['temperature_controller']:
            try:
                self.temperature_controller.set_temperature(room_temp)
            except ValueError:
                logging.warning("Temperature Controller not working")
            except OSError:
                logging.warning("Temperature Controller not working")
            except IOError:
                logging.warning("Temperature Controller not working")
        #Home stage
        with self.device_locks['stage']:
            self.stage.home()
        #Turn off light source
        light_source(self.gpio_interface, self.light_source_1_pin, self.light_source_2_pin, False, False)
        #Set the reactor back to idle
        self.status_code = status_codes[5]
        #Set status values back to none
        self.step = None
        self.total_steps = None
        self.run_uuid = None
        return