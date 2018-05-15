# chemios

Chemios is a python package for automated control of laboratory equipment.  We are in the process of open sourcing this package. 


## [controller](./chemiosbrain/controller.py)

This is the main module in chemiosbrain. It currently has two classes: Reactor, which is a general abstraction of a reactor, and FlowReactor, which inherits reactor and represents our first flow reactor. Flowreactor takes care of communicating with the pumps, temperature controller, light sources and spectrometer. It also manages the state of the reactor, so you don't have to.

You interact with either class as follows:  

1. Create an instance of a reactor (e.g., flow_reactor) passing the appropriate parameters/objects.
2. Update any needed parameters (e.g., blank spectrometer data, stage positions).
3. Add a new procedure or single instruction via the new_instruction method.
4. Call next() to advance through the procedure or the instruction.
5. "Run Complete" or "Instruction Complete" will be returned by next() once there are no more steps left.

For example:

    from chemiosbrain.controller import Reactor
    import uuid
    from pprint import pprint

    id = hex(uuid.getnode())
    ip = '192.168.1.1'
    reactor = Reactor(id, ip)
    instruction = {
                    "type": "single instruction",
                    "instruction": {
                      "pump_1_rate": 120.1,
                      "pump_2_rate": 60,
                      "pump_3_rate": 4.25,
                      "temp_setpoint": 90,
                      "light_source_1_on": true,
                      "light_source_2_on": false,
                      "uv_spec_integration_time": 3000,
                      "uv_spec_scans_to_average": 12,
                      "viewing_port_number": 2
                      }
                    }
     response = reactor.new_instruction(instruction)
     print(response)  #Should return "Single Instruction Created"
     response = reactor.next()
     print(response) #Should return "Next Step Initiated"
     status = reactor.get_status()
     #Should yield a json object with a status update.
     #See tests/sample_data/status_update_instruction for an example
     pprint(status)  

## [pump_control](./chemiosbrain/pump_control.py)

The pump_control module supports control of the pumps.  Primarily, we are using the Chemyx OEM pump. You can interact with the pumps as follows:

    from chemiosbrain.pump_control import pump
    import serial
    import time

    #Instantiate serial and pump
    serial_port = '/dev/ttyUSB0'
    ser = serial.Serial(serial_port, timeout=3)
    pump_1 = pump(model = 'Chemyx', 
                  address = 1, 
                  diameter = 30, 
                  ser = ser)

    #Set pump 1 infuse at 100 microliters/minute
    rate_1 = {'value': 100, 'units': 'UM'}
    pump_1.set_rate(rate_1, 'INF')

    #Run pump
    pump_1.run()
    time.sleep(5)

    #Stop the pump
    pump.stop()  

For prototypeonemain.py, we use the [pump_config](./prototype/pump_config.json) file to specify pump parameters.

Note about Chemyx pumps: Unfortunatley, the Cheymxy pumps do not have an address feature, so we had to come up with a workaround.  Currently,each pump is set to different units (internally in the pump_controll class), and the proper unit conversions are programme in. We read those units at startup to determine the "address".  So address 0 corresponds with pump 1 and address 2 corresponds with pump 2. 

## [temperature_controller](./chemiosbrain/temperature_controller.py)

Our temperature control system design is based around the Omega CN9311 temperature controller. For more information on the wiring of the temperature controller see the [hardware repo](https://gitlab.com/chemios/chemios-hardware/tree/master/temperature-controller).

The CN9311 uses the Modbus, a serial protocol developed for communication between industrial control systems. [This website](http://www.simplymodbus.ca/FAQ.htm#Modbus) gives a good overview of the protocol.

The [Omega Modbus Manual](./manuals/omegaModbusManual.pdf) explains the Omega implementation ModBus protocol. There is a python library for ModBus called [MinimalModbus](https://minimalmodbus.readthedocs.io/en/master/), and they have an [example](https://minimalmodbus.readthedocs.io/en/master/apiomegacn7500.html) for an Omega temperature controller (though it's not the CN9311).


## [spectrometer](./chemiosbrain/spectrometer.py)

This class maintains the spectrometer information, including buffering spectra as necessary.

## [utils](./chemiosbrain/utils.py)

These are utilities for serial communication and interacting with the Ocean Optics Spectrometer.

## Documentation

We are still working on this. For now, look at the docstrings (we are using the [Google Docstrings protocol](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)) and trying to follow the [pep-8 style guide](https://www.python.org/dev/peps/pep-0008/).

## Contributing

Please, do not push substantial changes directly to master (a substantial change is anything besides updating a README or docstring). Instead, create a branch in the format `your_name-feature`. So, if Kobi is working on a feature called foo, his branch would be `kobi-foo`. Then, submit a merge request (same as a pull request on Github) and assigned it to @marcos_felt.

