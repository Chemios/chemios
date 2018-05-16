![Chemios Framework ReadMe Banner](./assets/framework_readme_banner.jpg)

 **Chemios Framework** — Control pumps, spectrometers, reactors and more through one easy-to-use software package.
 
 The Chemios Framework takes care of the idiosyncrancies of interfacing with each piece of lab equipment, so you can focus automating your experiments. 

 
 The framework is written in python (the unoffical language of science), made open-source and is actively maintained.


## Contents

 - Quick Start
 - Examples
 - Features
 - Contributing


## 🗒 [pump_control](./chemiosbrain/pump_control.py)

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

