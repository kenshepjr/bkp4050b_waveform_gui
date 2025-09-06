'''
This program is intended to be a stand-alone module to interact with the BK Precision 4054B Arbitrary Waveform Generator
Author: Kenneth Shepherd Jr
Version 1
Date Created: 2024/12/19
'''

import numpy as np
import time
import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

#import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# import equipment modules
import pack_BKP_4054B as BKP


# plot config
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['axes.labelsize'] = 10 
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['black'])
plt.rcParams['lines.markersize'] = 2

figsize_x = 5
figsize_y = 3




class BKP_4054B_GUI(tk.Frame):
    """ Class for interfacing with the BK precision arb waveform generator"""

    def __init__(self, master, name, Data):
        tk.Frame.__init__(self, master)
        self.master = master
        self.name = name
        self.Data = Data
        
        # dictionary values for the arb waveform generator
        self.keys = {}
        self.keys = ['num_cyc', 'period', 'amp', 'ofst', 'DTY_cyc', 'pulse_width', 'trg_dlay']

        # dictionary values for the table
        self.label_names = {}
        self.label_names = ['User Values', 'Waveform Values', 'Num Cycles (#)', 'Period (s)', 'Amplitude (V)', 'Offset (V)', 'Duty Cycle (%)', 'Pulse Width (s)', 'Trigger Delay (s)']

        #################
        ### Variables ###
        #################
        self.entry = {}
        
        self.Out_Display = tk.StringVar(master)  # Message On Output Enable Button
        self.Status_Display = tk.StringVar(master)  # Message On Status Display
        self.Status_Color = tk.StringVar(master)  # Color of status indicator
       
        # creates entry boxes for the keys
        for i, key in enumerate(self.keys, 0):
            self.entry[key] = tk.DoubleVar(master, Data.input_var[key].get())
                        
        
        ############################
        ### Waveform Display     ###
        ############################
        
        wavetypes = ['Square Wave', 'Pulse Wave', 'Pump TTIP Lines', 'Reset']
        
        self.BKP_Frame = tk.LabelFrame(master, text='BKP 4058B Supply', labelanchor='nw')
        self.BKP_Frame.grid(row=0, column=0, columnspan=2, sticky=tk.W+tk.E, padx=10, pady=10)
        
        self.combo = ttk.Combobox(self.BKP_Frame, values=wavetypes)
        self.combo.grid(row=0, column=1, padx=10, pady=10)
        self.Radio_Label = tk.Label(self.BKP_Frame,text='Choose A Waveform').grid(row=0, column=0)
        self.combo.bind('<<ComboboxSelected>>', self.on_select)
        
        # Paramters frame
        self.Parameters_Frame = tk.LabelFrame(master, text='Parameters', labelanchor='nw')
        self.Parameters_Frame.grid(row=1, column=0, sticky=tk.W+tk.E, padx=10, pady=10)
        
        # Table labels
        self.label = {}
        
        # creates the labels for each column and rows
        for i, names in enumerate(self.label_names, 0):
            if i == 0:
                self.label['user_vals'] = tk.Label(self.Parameters_Frame, text=names).grid(row=0, column=2, padx=10)
            elif i == 1:
                self.label['arb_values'] = tk.Label(self.Parameters_Frame, text=names).grid(row=0, column=3)
            else:
                self.label[self.keys[i-2]] = tk.Label(self.Parameters_Frame, text=names).grid(row=i-1, column=1)

                
        # User input values
        column_user_values = 2
        self.BKP = {}
        
        ## creates entries and binds them to a variable starting at row 1
        for i, key in enumerate(self.keys, 1):
            self.BKP[key] = tk.Entry(self.Parameters_Frame, textvariable=self.entry[key])
            self.BKP[key].bind('<Return>', lambda event, key=key: self.callback(self.entry[key], self.Data.input_var[key]))
            self.BKP[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.entry[key], self.Data.input_var[key]))
            self.BKP[key].grid(row=i, column=column_user_values, padx=5, pady=5)

        
        # read only values (RO)
        column_read_only = 3
        self.BKP_RO = {}
        
        # creates a read only column based on keys
        for i, key in enumerate(self.keys, 1):
            self.BKP_RO[key] = tk.Entry(self.Parameters_Frame, textvariable=self.Data.read_only[key])
            self.BKP_RO[key].config(state='readonly')
            self.BKP_RO[key].grid(row=i, column=column_read_only, padx=10, pady=5)
            
        
        # button to send wave
        self.button = tk.Button(self.Parameters_Frame, text='Ch1 Trigger', command=lambda: self.send_ch1_wave())
        self.button.grid(row=9, column=3)
    
    def callback(self, a, b):
        """ Sets the set-point variable when entry-box is change after pressing enter """
        b.set(a.get())
        
    def off_click(self,a , b):
        """ Reset Entry Box to correct value when clicking off the entry box. This prevent the box from displaying a not current value"""
        a.set(b.get())
        
    def send_ch1_wave(self):
        print('Sending channel 1 wave')
        BKP_wave.ch1_trigger()
            
    def on_select(self, event):
        '''Sets the waveform generator to the waveforms in the drop down menu'''
        self.selected_item = self.combo.get()
        if self.selected_item == 'Pulse Wave':
            BKP_wave.pulse_wave()
                        
        if self.selected_item == 'Square Wave':
            BKP_wave.square_wave()
            
        if self.selected_item == 'Pump TTIP Lines':
            BKP_wave.pump_TTIP_lines()
       
        if self.selected_item == 'Reset':
            BKP_wave.reset_controller()
            

class Data_Structure_BK4058B:
    """ Class to store global data used in GUI and to save logged data"""    
    
    def __init__(self, name):
        # Meta Data
        self.name = name
        
        # copied from BKP GUI
        self.keys = {}
        self.keys = ['num_cyc', 'period', 'amp', 'ofst', 'DTY_cyc', 'pulse_width', 'trg_dlay']
        
        # read only and input dictionaries
        self.read_only = {}
        self.input_var = {}
        
        for key in self.keys:
            self.read_only[key] = tk.DoubleVar()
            self.input_var[key] = tk.DoubleVar()

    
    
#############################################################################################
#############################################################################################     
        
    
#--------------------------------------------------------------------------------------------------------    
    
####################
### Main Program ###
####################
        
if __name__=='__main__':    
    root = tk.Tk()
    root.title('BK Precision 4054B Arbitrary Waveform Generator')
    
    SaveName = tk.StringVar(root)
    Clock = tk.StringVar(root,'0')
    Data_Num = tk.IntVar(root, 0)
    
#    # save function
#    def save_data(Data):
#        tmp = datetime.datetime.now()
#        date_time_stamp = f'{tmp.year}_{tmp.month:02d}_{tmp.day:02d}-{tmp.hour:02d}_{tmp.minute:02d}_{tmp.second:02d}_'
##        SaveName = date_time_stamp + 'Substrate_Heater_Test'
#        SaveName2 = date_time_stamp + SaveName.get()
#        if len(Data) > 1:
#            SaveData = np.hstack([Data[i] for i in range(len(Data))])
#        else:
#            SaveData = Data[0]
#        print (SaveName2)
#        print (SaveData.shape)
#        np.save(SaveName2, SaveData)
        
    # quit function
    def _quit():
        # close serial connections
        BKP_wave.close() 

        
        # save data
#        save_data([])
        
        # close application
        root.quit()
        root.destroy()  # prevent fatal error

    
    #############################################   
    ### Initialize Variables and Data Storage ###
    #############################################
    t0 = time.time()
    dt = 1000//10  # update time in milliseconds
    
    # initialize controller
    
    ports = {}
    ports['BKP Wave'] = "USB0::0xF4EC::0xEE38::515E21166::INSTR"
    
    Waveform_data = Data_Structure_BK4058B('BKP 4058B Waveform Generator')
           
    # BK Precision Arb Waveform Generator
    BKP_wave = BKP.BKP_waveform_generator(ports['BKP Wave'])
    Waveform_data.read_only['num_cyc'].set(BKP_wave.get_params('BTWV', 'TIME'))
    Waveform_data.read_only['period'].set(BKP_wave.get_params('BSWV', 'PERI'))
    Waveform_data.read_only['amp'].set(BKP_wave.get_params('BSWV', 'AMP'))
    Waveform_data.read_only['ofst'].set(BKP_wave.get_params('BSWV', 'OFST'))
    Waveform_data.read_only['DTY_cyc'].set(BKP_wave.get_params('BTWV', 'DUTY'))
    Waveform_data.read_only['pulse_width'].set(BKP_wave.get_params('BSWV', 'WIDTH'))
    Waveform_data.read_only['trg_dlay'].set(BKP_wave.get_params('BTWV', 'DLAY'))    
    
    #########################   
    ### Create GUI Layout ###
    #########################   
    # MKS = Baratron Controller
    # BKP = BK precission arb waveform generator
    
    window = {}
    GUI = {}
    Width = 700
    Height = 700
       
    # Arb Waveform GUI
    window['BKP GUI'] = tk.LabelFrame(root, text='BK Waveform Generator', font=('Helvetica', 15, 'bold'), labelanchor='n', width=Width, height=Height)
    window['BKP GUI'].grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    
    GUI['BKP'] = BKP_4054B_GUI(window['BKP GUI'], 'Wave Generator', Waveform_data)
    GUI['BKP'].grid(row=0, column=0)
    
    # Clock Display
    window['remaining widgets'] = tk.LabelFrame(window['BKP GUI'], text='Widgets', font=('Helvetica', 15, 'bold'), labelanchor='n')
    window['remaining widgets'].grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
    
    Clock_Label = tk.Label(window['remaining widgets'], text='Clock (min)').grid(row=3 ,column=0, pady=5)
    Clock_Display = tk.Entry(window['remaining widgets'], textvariable=Clock,font=('Helvetica', 13))
    Clock_Display.config('readonly')
    Clock_Display.grid(row=3, column=1, padx=5, pady=5)
    
    # Data Point Display
    Data_Point_Display = tk.Label(window['remaining widgets'], text='Data Point').grid(row=4, column=0, pady=5)
    Data_Point = tk.Entry(window['remaining widgets'], textvariable=Data_Num, font=('Helvetica', 13))
    Data_Point.config('readonly')
    Data_Point.grid(row=4, column=1, padx=5, pady=5)
    
    # Quit Button   
    Q_button = tk.Button(window['remaining widgets'], text='Quit',command=_quit, font=20, width=20)
    Q_button.grid(row=6, column=1, padx=5, pady=5)

    
    ########################
    ### Events and Loops ###
    ########################
    
    #################################
    ###### Arb Waveform  ############    
    #################################    

    def set_Ncycle(BKP_4058B, data):
        BKP_4058B.set_num_cyc(data.input_var['num_cyc'].get())
    
    def set_PERI(BKP_4058B, data):
        BKP_4058B.set_period(data.input_var['period'].get())
        
    def set_AMP(BKP_4058B, data):
        BKP_4058B.set_amplitude(data.input_var['amp'].get())
        
    def set_OFFSET(BKP_4058B, data):
        BKP_4058B.set_offset(data.input_var['ofst'].get())

    def set_DUTY_CYCLE(BKP_4058B, data):
        BKP_4058B.set_duty_cycle(data.input_var['DTY_cyc'].get())
        
    def set_PULSE_WIDTH(BKP_4058B, data):
        BKP_4058B.set_pulse_width(data.input_var['pulse_width'].get())
        
    def set_TRG_DLAY(BKP_4058B, data):
        BKP_4058B.set_trigger_delay(data.input_var['trg_dlay'].get())
        
    Waveform_data.input_var['num_cyc'].trace('w', lambda a, b, c: set_Ncycle(BKP_wave, Waveform_data))
    Waveform_data.input_var['period'].trace('w', lambda a, b, c: set_PERI(BKP_wave, Waveform_data))
    Waveform_data.input_var['amp'].trace('w', lambda a, b, c: set_AMP(BKP_wave, Waveform_data))
    Waveform_data.input_var['ofst'].trace('w', lambda a, b, c: set_OFFSET(BKP_wave, Waveform_data))
    Waveform_data.input_var['DTY_cyc'].trace('w', lambda a, b, c: set_DUTY_CYCLE(BKP_wave, Waveform_data))
    Waveform_data.input_var['pulse_width'].trace('w', lambda a, b, c: set_PULSE_WIDTH(BKP_wave, Waveform_data))   
    Waveform_data.input_var['trg_dlay'].trace('w', lambda a, b, c: set_TRG_DLAY(BKP_wave, Waveform_data))    
    
    # Update Loop
    def update(t0):
        """ updates the data values after a pre-set time dt"""       
        
        # Update variables for BK 4048B
        Waveform_data.read_only['num_cyc'].set(BKP_wave.get_params('BTWV', 'TIME'))
        Waveform_data.read_only['period'].set(BKP_wave.get_params('BSWV', 'PERI'))
        Waveform_data.read_only['amp'].set(BKP_wave.get_params('BSWV', 'AMP'))
        Waveform_data.read_only['ofst'].set(BKP_wave.get_params('BSWV', 'OFST'))
        Waveform_data.read_only['DTY_cyc'].set(BKP_wave.get_params('BSWV', 'DUTY'))
        Waveform_data.read_only['pulse_width'].set(BKP_wave.get_params('BSWV', 'WIDTH'))
        Waveform_data.read_only['trg_dlay'].set(BKP_wave.get_params('BTWV', 'DLAY'))
        
        
#        # Update plots
#        GUI['BKP']._update()
        
        # Update Clock and Data Point Counter
        Clock.set(str((time.time()-t0)/60)[:-10])
        Data_Num.set(Data_Num.get()+1)
        
        # Continue Loop
        root.after(dt, lambda: update(t0)) 
        
        
    root.after(0, lambda: update(t0))
    
    # Start main Loop
    root.protocol('WM_DELETE_WINDOW', _quit)
    root.mainloop()
    
