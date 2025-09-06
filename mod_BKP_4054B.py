# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 07:35:07 2024

@author: Kenneth Shepherd jr 
Interfaces with the BK precision Arb Waveform Generator 
"""

import pyvisa as py
import re
import numpy as np


# definitions
query = "*IDN?"


class BKP_waveform_generator:
    '''Library of definitions to communicate with the waveform generator'''
    
    def __init__(self, port):
        
        self.rm = py.ResourceManager()
        # open the waveform generator port and print the ID of the controller
        self.wave_generator = self.rm.open_resource(port)
        print("Here is your waveform generator ID: ", self.wave_generator.query("*IDN?")) 
        self.wave_generator.write("*RST; status::present;*CLS")
        self.wave_generator.write("C1:OUTP OFF")
        self.wave_generator.write('C2:OUTP OFF')
        self.wave_generator.write("C1:BTWV STATE, OFF")
        self.wave_generator.write('SCSV OFF')
        
    def pulse_wave(self):
        self.wave_generator.write("*RST; status::present;*CLS")
        self.wave_generator.write("C1:BSWV WVTP, PULSE")        
        self.wave_generator.write("C1:BTWV STATE, ON")
        self.wave_generator.write("C1:BTWV TRSR, MAN")
        self.wave_generator.write("C1:BTWV GATE_NCYC, NCYC")
        self.set_amplitude(5)
        self.wave_generator.write("C1:OUTP ON")    


    def square_wave(self):
        self.wave_generator.write("*RST; status::present;*CLS")
        self.wave_generator.write("C1:BSWV WVTP, SQUARE")
        self.wave_generator.write("C1:BTWV STATE, ON")
        self.wave_generator.write("C1:BTWV TRSR, MAN")
        self.wave_generator.write("C1:BTWV GATE_NCYC, NCYC")
        self.wave_generator.write("C1:OUTP ON")
        
    def pump_TTIP_lines(self):
        self.wave_generator.write("*RST; status::present;*CLS")
        self.wave_generator.write("C1:BSWV WVTP, PULSE")        
        self.wave_generator.write("C1:BTWV STATE, ON")
        self.wave_generator.write("C1:BTWV TRSR, MAN")
        self.wave_generator.write("C1:BTWV GATE_NCYC, NCYC")
        self.set_amplitude(5)
        self.set_num_cyc(144)
        self.set_period(400)
        self.set_duty_cycle(100/400*100)
#        self.wave_generator.write("C1:OUTP ON") 


    def get_params(self, wave, parameter):
        '''Request the follow keywords for paramters TIME, PERI, DUTY and returns the value as a string'''
        query_request = self.wave_generator.query('C1:' + wave + '?')
        params = ['TIME', 'DLAY', 'FRQ', 'AMP', 'OFST', 'DUTY', 'PERI', 'WIDTH', 'C1:BTWV STATE']
        param_values = {}
        
         # extract the paramters values using regex
        for param in params:
            match = re.search(f'{param},([^,]+)', query_request)
            if match:
                param_values[param] = match.group(1)
            
#        print('here are the param values', param_values)
        
        try:
            if parameter in param_values:
                value = param_values[parameter]
                if parameter in ['TIME', 'DUTY', 'WIDTH']:
                    return value
                elif parameter == 'DLAY':
                    return value[:-1]
                else:
                    return value[:-1]
            else:
                return np.nan
        except KeyError:
            return np.nan
        
    def set_num_cyc(self, ncycle):
        self.wave_generator.write("C1:BTWV TIME," + str(ncycle))
        
    def set_period(self, T):
        '''Sets the period in the waveform generator. Default units are seconds'''
        self.wave_generator.write("C1:BSWV PERI," + str(T))
        
    def set_amplitude(self, A):
        '''Sets the amplitude in the waveform generator. Default units are volts'''
        self.wave_generator.write("C1:BSWV AMP," + str(A))        
    
    def set_offset(self, off):
        '''Sets the offset in the waveform generator. Default units are volts'''
        self.wave_generator.write('C1:BSWV OFST,' + str(off))
        
    def set_duty_cycle(self, DTY):
        '''Sets the duty cycle in the waveform generator in percentage'''
        self.wave_generator.write('C1:BSWV DUTY,' + str(DTY))
        
    def set_pulse_width(self, width):
        '''Sets the pulse width in the waveform generator. Default units are seconds'''
        self.wave_generator.write('C1:BSWV WIDTH,' + str(width))
    
    def set_trigger_delay(self, delay):
        '''Sets the trigger delay'''
        if delay < 3e-07:
            self.wave_generator.write('C1:BTWV DLAY,' + str(3e-07))
        else:
            self.wave_generator.write('C1:BTWV DLAY,' + str(delay))
            
    def ch1_trigger(self):
        self.wave_generator.write('C1:BTWV MTRIG')

    def reset_controller(self):
        self.wave_generator.write("*RST; status::present; *CLS")
        self.wave_generator.write("C1:OUTP OFF")
        self.wave_generator.write("C2:OUTP OFF")
        
    def close_cont(self):
        print("Closing the program and the connection")
        self.wave_generator.write("*RST; status::present;*CLS")
        self.wave_generator.write("C1:OUTP OFF")
        self.wave_generator.write("C2:OUTP OFF")
        self.wave_generator.close()
        self.rm.close()
    