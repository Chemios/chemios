# Brain

The Chemios Brain is a raspberry pi 3 (RPi3) running python code that controls our reactors. 

prototypes/prototypeonemain.py is the file that main file used to control the device. It interacts with AWS IoT using the [AWS IoT python SDK](https://github.com/aws/aws-iot-device-sdk-python) to receive instructions/procedures from and send data to our web app. The chemiosbrain package takes care of communicating with each piee of reactor equipment and keeping track of the state of the reactor.


## resin.io

We are using [resin.io](https://resin.io/) to for over-the-air deployment of the application to the RPi3. Resin relies on docker containers to ensure consistency between your dev environment and the RPi3.  

To use resin, first install the resin cli as shown in [resin's documentation](https://docs.resin.io/reference/cli/) (copied for your convience below):

    $ npm install resin-cli -g --production --unsafe-perm

You will need to login to resin.io using the command `resin login`. Contact @marcos_felt for credentials.

Before deploying to RPi3, you need to a docker image of the repository. You can either `docker pull registry.gitlab.com/chemios/chemios-firmware:latest` to get latest stable image from our [container registry](https://gitlab.com/chemios/chemios-firmware/container_registry) and then run

    $ sudo resin deploy chemiosnano registry.gitlab.com/chemios/chemios-firmware:latest

Or, you can build the image yourself by running the following command in the root of this repository:

    $ sudo resin build -A armv7l -d raspberrypi3 -e .

Then, to deploy to the RPi3, use the following command:

    $ sudo resin deploy chemiosnano -A armv7l -d raspberrypi3 -e .

You can then go to the [resin dashboard](https://dashboard.resin.io/) to see the status of the RPi3 and ssh into the device.

## prototype one

[prototypeonemain.py](./prototype/prototypeonemain.py) is the true brain of the reactor. It runs at startup in the docker container.

prototypeonemain.py gets settings from environmental variables and config files. The environmental variables are below.  Note that the serial ports are not necessary, since the code can automatically discover the ports. 

    #Stage is DEV, TEST or PROD. Sets the log levels and location of the lockfile (to prevent resin.io from updating while the reactor is running)
    export STAGE="DEV"  
    export UUID="12ke3lkjdslfkjsa"       # UUID of the reactor
    
    #Endpoint from the AWS IoT console. Check here for the actual endpoint: https://us-east-2.console.aws.amazon.com/iotv2/home?region=us-east-2#/.
    export AWS_IOT_ENDPOINT="abcdef.iot.us-east-2.amazonaws.com"   

    #Acess keys for AWS. See raspberry-pi IAM user for actual keys
    export AWS_ACCESS_KEY_ID='123456'
    export AWS_SECRET_ACCESS_KEY='1234567'
    
    #Choose whether to backup spectrum data locally
    #Note that in dev this just creates a generic file, but in test and production,
    #it saves a unique file for each run in the resinOS permanent storage (/mnt/data/resin-data/<APP ID>)
    export SAVE_TO_FILE="True"

To find local serial ports:

* Linux: Run `dmesg | grep tty`.  The ports are incremented by the order in which devices are connected.
* Mac: Run `ls /dev/cu*`

To run the prototype during development:

    pip install -r requirements-dev.txt #Install requirements
    pip install -e .  #Install the chemiosbrain package
    cd prototype
    python protototypeonemain.py

Notes for development
* You must be running python 3.0 or higher.
* You can test prototypeonemain.py without any of the devices (e.g., pumps, spectrometer, etc.) connected. It will just used mock classes to represent those devices. 
* python-seabreeze and RPi.GPIO are not installed during local dev.  The prototypeonemain.py script can run without these installed using the mock classes in prototype/mocks_for_controller.py.  If you want to test thse, deploy to the RPi (noted above). 

## chemiosbrain package

chemiosbrain is a package that contains important modules for controlling our reactors.  

### [controller](./chemiosbrain/controller.py)

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

### [pump_control](./chemiosbrain/pump_control.py)

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

### [temperature_controller](./chemiosbrain/temperature_controller.py)

Our temperature control system design is based around the Omega CN9311 temperature controller. For more information on the wiring of the temperature controller see the [hardware repo](https://gitlab.com/chemios/chemios-hardware/tree/master/temperature-controller).

The CN9311 uses the Modbus, a serial protocol developed for communication between industrial control systems. [This website](http://www.simplymodbus.ca/FAQ.htm#Modbus) gives a good overview of the protocol.

The [Omega Modbus Manual](./manuals/omegaModbusManual.pdf) explains the Omega implementation ModBus protocol. There is a python library for ModBus called [MinimalModbus](https://minimalmodbus.readthedocs.io/en/master/), and they have an [example](https://minimalmodbus.readthedocs.io/en/master/apiomegacn7500.html) for an Omega temperature controller (though it's not the CN9311).

### [valve_control](./chemiosbrain/valve_control.py)

@srhollan Can you add a description of valve_control here?

### [spectrometer](./chemiosbrain/spectrometer.py)

This class maintains the spectrometer information, including buffering spectra as necessary

### [utils](./chemiosbrain/utils.py)

These are utilities for serial communication and interacting with the Ocean Optics Spectrometer.

## Documentation

We are still working on this. For now, look at the docstrings (we are using the [Google Docstrings protocol](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)) and trying to follow the [pep-8 style guide](https://www.python.org/dev/peps/pep-0008/).

## Contributing

Please, do not push substantial changes directly to master (a substantial change is anything besides updating a README or docstring). Instead, create a branch in the format `your_name-feature`. So, if Kobi is working on a feature called foo, his branch would be `kobi-foo`. Then, submit a merge request (same as a pull request on Github) and assigned it to @marcos_felt or @snrathod.

## To-Do
Check in trello for the most up-to-date list of to-dos, but the following is an overall roadmap.

- [x] Write class for controlling NE-100
- [x] Add Wire commands for controlling DIY syringe pump
- [x] Write commands for gathering data from the Ocean Optics Spectrometer
- [x] Write wire commands for turning on/off light source
- [x] Write AWS IoT interpreter
- [x] Refactor code to fit the pep-8 standards and package chemiosbrain
- [x] Create prototypetwomain.py to communicate with AWS IoT @snrathod
- [x] Write temperature_controller module @jeff_b62
- [ ] Document all code and start a sphinx page @cchillen
