![Chemios Framework ReadMe Banner](./assets/framework_readme_banner.jpg)

[![CircleCI](https://circleci.com/gh/Chemios/chemios.svg?style=svg)](https://circleci.com/gh/Chemios/chemios)

**Chemios Framework** — The automation and monitoring solution for laboratories.
 
**The Problem**:
Laboratories have a lot of equipment—pumps, spectrometers, incubators, etc. One laboratory's equipment is usually worth millions of dollars.

Despite their price tag, these devices are rarely smart. You have to monitor them in person and transfer data using USBs or, worse, floppy disks. You do not get alerted when something goes wrong. And do not mention coordinating a complex automated experiment—you'd need a couple months or years for that.

Currently, there is not a simple, open source framework for lab monitoring and automation. Tetrascience is a paid monitoring platform that is [unaffordable for most labs][nature]. Labview has been used to automate lab equipment (see [Epps et al.][epps], [Reizman et al.][reizman], or [Dragone et al.][dragone]). However, LabView binaries are cumbersome, and licenses with distribution rights cost $5000 annually. ThermoFisher Cloud is the closest, and it only works with ThermoFisher products.

**The Solution**:
 The Chemios Framework is a simple, open-source (i.e. FREE) software package for laboratory automation and monitoring. It is easy-to-use and extensible. It currently works with pumps, spectrometers and temperature controllers; more devices will be added to the roadmap based on feedback from users.

 The framework is written in python (the unoffical language of science) and actively maintained. 

## Contents

 - 🛠️ [Installation](#installation)
 - 👍 [Examples](#examples)
 - ⚙️ [Compatabile Equipment](#features)
 - 🎁 [Contributing](#contributing)


## 🛠️<a name="installation"></a> Installation

Follow the steps below to design and run your first experiment in minutes.

1. [Install python](https://www.python.org/downloads/) (version 3 or above) if you haven't already. If you are using Windows, it is recommended to install python in the [cygwin](https://cygwin.com/install.html) terminal.
2. Download (via the green button above) this repository or clone it:
    ```bash
    $ git clone https://github.com/Chemios/chemios.git
    ````
3. Enter into the root of the repository directory and run:
    ```bash
    pip install e .;  pip install -r requirements.txt
    ```

## 👍 <a name="examples"></a> Examples

Here is a how you'd use chemios to run a pump in an automated fashion.

```python
from chemios.components.pumps import HarvardApparatus
from time import sleep
import serial

#Set up serial port for communciation with pump over USB
ser = serial.Serial(port='ttyUSB0', timeout=1, baudrate=9600)

#Connect to a Harvard Apparatus PhD Ultra
C = Chemyx(model='Phd-Ultra', ser=ser, 
           syringe_manufacturer='Hamilton', syringe_volume=10)

#Set the flowrate to infuse at 100 microliters per minute
rate = {'value': 100,
        'units': UM}                     
C.set_rate(rate=rate
            direction = 'INF')

#Run the pump for 5 seconds
C.run()
sleep(5)

#Stop the pump
C.stop()
```

## ⚙️ <a name="features"></a> Compatible Equipment

- Chemios currently works with the following types of devices:
     * Syringe Pumps: Harvard Apparatus, Chemyx, and New-Era
     * Spectrometers: Ocean Optics 
     * Temperature Controllers: Omega CN 9300 Series

- Roadmap:
     * Finish unit testing syringe pumps
     * Create device framework for automating experiments and reactors
     * Add more devices


## 🎁 <a name="contributing"></a> Contributing

We ❤️ contributors!

We are looking in particular for people to extend the framework to work with more types of laboratory equipment. To contribute, fork the repository, make your changes and submit a pull request. [This](https://gist.github.com/Chaser324/ce0505fbed06b947d962) is a nice set of instructions on how to do that.  We'll review the changes and add them to the library.

[nature]: https://www.nature.com/news/the-internet-of-things-comes-to-the-lab-1.21383?WT.feed_name=subjects_technology#thecostofmonitoring
[reizman]: https://pubs.acs.org/doi/10.1021/acs.accounts.6b00261
[dragone]: https://www.nature.com/articles/ncomms15733
[epps]: http://pubs.rsc.org/en/content/articlelanding/2017/lc/c7lc00884h