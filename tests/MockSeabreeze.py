'''
/*
 * Copyright 2018 Chemios
 * Chemios Spectrometer
 *
 * Methods to control an Ocean Optics Spectrometer
 *
 */
 '''
import pandas as pd

#File paths
sample_spectrometer_data = './sample_data/sample_spectrometer_data.csv'

class Spectrometer(object):
    def __init__(self):
        df = pd.read_csv(sample_spectrometer_data)
        self.wavelength_values = df.wavelength.values.tolist()
        self.intensity_values = df.intensity.values.tolist()

    @classmethod
    def from_serial_number(cls, spectrometer_model):
        if isinstance(spectrometer_model, str): 
            return cls()

    def integration_time_micros(self, integration_time):
        return

    def wavelengths(self):
        return self.wavelength_values

    def intensities(self, correct_dark_counts, correct_nonlinearity):
        return self.intensity_values
    
    def close(self):    
        return
