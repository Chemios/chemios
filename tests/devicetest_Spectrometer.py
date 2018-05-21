from chemiosbrain.spectrometer import Spectrometer
from chemiosbrain.utils import convert_to_lists
import seabreeze.spectrometers as sb
import unittest
import pandas as pd
import sys

#Need python3 for some of the methods used in unittest
assert sys.version_info >= (3, 0)
#Class to test spectrometer using the MockSeabreeze class

sample_blank_file_csv = './sample_data/sample_blank_data.csv'
sample_dark_file_csv = './sample_data/sample_dark_data.csv'


class TestSpectrometer(unittest.TestCase):
    #Set up the spectrometer unit test
    def setUp(self):
        self.spec = Spectrometer("FLMS02673", sb)
        df = pd.read_csv(sample_blank_file_csv)
        self.blank = convert_to_lists(df)
        df = pd.read_csv(sample_dark_file_csv)
        self.dark = convert_to_lists(df)       

    def tearDown(self):
        del self.spec

    #Check the raw spectrometer reading is working properly
    def test_read_spectrometer_raw(self):
        with self.spec as spec:
            spec.read_spectrometer_raw(1000)

    #Check that you can store blank
    def test_blank_intensities(self):
        with self.spec as spec:
            spec.store_blank(self.blank)

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
            output = spec.absorbance_read(integration_time=1000, 
                                          scans_to_average = 10,
                                          filter = 300,
                                          normalized = False)
            print(output)
            spec.absorbance_read(integration_time=1000, 
                                          scans_to_average = 10,
                                          filter = 300,
                                          normalized = True)

if __name__ == "__main__":
    unittest.main()