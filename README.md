![Chemios Framework ReadMe Banner](./assets/framework_readme_banner.jpg)

[![CircleCI](https://circleci.com/gh/Chemios/chemios.svg?style=svg)](https://circleci.com/gh/Chemios/chemios)
[![Documentation Status](https://readthedocs.org/projects/chemios/badge/?version=latest)](https://chemios.readthedocs.io/en/latest/?badge=latest)

## Contents
 - 👨🏾‍🔬 [Why Chemios?](#why-chemios)
 - 🛠️ [Installation](#installation)
 - 👍 [Examples](#examples)
 - 📋 [Documentation](#documentation)
 - ⚙️ [Compatible Equipment](#features)
 - 🎁 [Contributing](#contributing)

## 👨🏾‍🔬 <a name="why-chemios"></a>Why chemios?

### The Problem
Laboratories have a lot of equipment—pumps, spectrometers, incubators, etc. One laboratory's equipment is usually worth millions of dollars.

Despite their price tag, these devices rarely have simple software interfaces. So, monitoring them remotely or integrating them into automated experiments is difficult. 

We looked at the existing solutions, and we were not satisfied. Tetrascience is a paid monitoring platform that is [unaffordable for most labs][nature]. Labview has been used to automate lab equipment (see [Epps et al.][epps], [Reizman et al.][reizman], or [Dragone et al.][dragone]). However, LabView licenses cost $5000 annually. ThermoFisher Cloud is the most promising solution, but it only works with a limited number of Thermofisher products.

### The Solution
The Chemios Framework is a simple, open-source (i.e. FREE) software package for laboratory automation and monitoring. It is easy-to-use and extensible. It currently works with pumps, spectrometers and temperature controllers. And, the list of equipment will continue to grow (see [Compatible Equipment](#features)) through an open source community. Please [submit an issue](https://github.com/Chemios/chemios/issues)

The framework is written in python (the unoffical language of science) and actively maintained. 

## 🛠️<a name="installation"></a> Installation

Follow the steps below to design and run your first experiment in minutes.

1. [Install python](https://www.python.org/downloads/) (version 3 or above) if you haven't already. If you are using Windows, it is recommended to install python in the [cygwin](https://cygwin.com/install.html) terminal.
2. Download this repository (via the green button above) or clone it:
    ```bash
    $ git clone https://github.com/Chemios/chemios.git
    ````
3. Enter into the root of the repository directory and run:
    ```bash
    pip install e .;pip install -r requirements.txt
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
## 📋 <a name="documentation"></a> Documentation

You can find documentation for the chemios framework [here](chemios.readthedocs.io). More examples will be added soon.

## ⚙️ <a name="features"></a> Compatible Equipment

- Chemios currently works with the following types of devices:
     * Syringe Pumps: Harvard Apparatus, Chemyx, and New-Era
     * Spectrometers: Ocean Optics 
     * Temperature Controllers: Omega CN 9300 Series

- You can vote for which equipment should be added next [here][gform]!

- Roadmap:
     * Finish unit testing syringe pumps (May 2018)
     * Add create-device script for easily creating a device (May 2018)
     * Publish package on PyPI (June 2018)
     * Create experiments module for automating (June 2018)
     * More to come based on your input.

## 🎁 <a name="contributing"></a> Contributing

We ❤️ contributors! The Chemios Framework came out of a senior design project at [NC State](https://www.ncsu.edu/) and is now maintained by Kobi Felton [@marcosfelt](https://github.com/marcosfelt).

We are looking in particular for people to extend the framework to work with more types of laboratory equipment. Feel free to [email Kobi](mailto:kobi.c.f@gmail.com) if you're interested.  If you already have some changes, please submit a [pull request](https://gist.github.com/Chaser324/ce0505fbed06b947d962).

[nature]: https://www.nature.com/news/the-internet-of-things-comes-to-the-lab-1.21383?WT.feed_name=subjects_technology#thecostofmonitoring
[reizman]: https://pubs.acs.org/doi/10.1021/acs.accounts.6b00261
[dragone]: https://www.nature.com/articles/ncomms15733
[epps]: http://pubs.rsc.org/en/content/articlelanding/2017/lc/c7lc00884h
[gform]: https://goo.gl/forms/BS2ZI7HK1Et4CMEl2
