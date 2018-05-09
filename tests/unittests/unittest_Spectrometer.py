'''
/*
 * Copyright 2018 Chemios
 * Chemios Spectrometer Tests
 *
 * Test of spectrometer.py
 *
 */
 '''
from chemiosbrain.spectrometer import Spectrometer
from chemiosbrain.utils import convert_to_lists
import MockSeabreeze
import unittest
import pandas as pd
import sys

#File paths
sample_spectrometer_data = './sample_data/sample_spectrometer_data.csv'
sample_blank_file_csv = './sample_data/sample_blank_data.csv'
sample_dark_file_csv = './sample_data/sample_dark_data.csv'

#Need python3 for some of the methods used in unittest
assert sys.version_info >= (3, 0)

#Class to test spectrometer using the MockSeabreeze clas
class TestSpectrometer(unittest.TestCase):
    #Set up the spectrometer unit test
    def setUp(self):
        self.model = 'LH1357'
        self.spec = Spectrometer(self.model, MockSeabreeze)
        df = pd.read_csv(sample_spectrometer_data)
        self.data = convert_to_lists(df)
        df = pd.read_csv(sample_blank_file_csv)
        self.blank = convert_to_lists(df)
        df = pd.read_csv(sample_dark_file_csv)
        self.dark = convert_to_lists(df)

    def tearDown(self):
        del self.spec

    #Check the raw spectrometer reading is working properly
    def test_read_spectrometer_raw(self):
        with self.spec as spec:
            output = spec.read_spectrometer_raw(1000)
        self.assertCountEqual(output[1],self.data[1])

    #Check that you can store blank
    def test_blank_intensities(self):
        self.spec.store_blank(self.blank)

    #Check that you can store dark
    def test_dark_intesities(self):
        with self.spec as spec:
            spec.store_dark(self.dark)

    #The MockSeabreeze class pull from the sample_spectrometer_data file
    #Mainly checking that you can call the functions here
    def test_absorbance_read(self):
        with self.spec as spec:
            spec.store_blank(self.blank)
            spec.store_dark(self.dark)
            output1 = spec.absorbance_read(integration_time=1000, 
                                          scans_to_average = 10,
                                          filter = 300,
                                          normalized = False)
            output2 = spec.absorbance_read(integration_time=1000, 
                                          scans_to_average = 10,
                                          filter = 300,
                                          normalized = True)

if __name__ == "__main__":
    unittest.main()
