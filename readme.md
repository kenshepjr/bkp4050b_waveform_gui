# BK Precision 4054B Arbitrary Waveform Generator GUI
This repository contains a standalone Python GUI for interfacing with the BK Precision 4054B Arbitrary Waveform Generator. Designed for scientific workflows, it enables waveform selection, parameter tuning, and synchronized controller readiness across multiple instruments.

## Features
- GUI built with tkinter and matplotlib
- Supports waveform types: Square, Pulse, Pump TTIP Lines, Reset
- Real-time parameter control: cycles, period, amplitude, offset, duty cycle, pulse width, trigger delay
- Read-only feedback from instrument
- Controller synchronization via signaling file
- Modular design for integration with other lab controllers

# Requirements
- Python 3.8+
- Required packages:  

```python
pip install numpy matplotlib tkinter datetime time
```

- BK Precision 4054B connected via USB (e.g., "USB0::0xF4EC::0xEE38::515E21166::INSTR")
    -   change line 274 for your port.
- Custom module: mod_BKP_4054B.py (must be included in the repo)

# Getting Started
- Clone the repository:
git clone https://github.com/your-username/BK_Arb_Waveform_GUI.git
cd BK_Arb_Waveform_GUI
- Run the GUI:
python cont_BK_Arb_Waveform_Generator_V3.py
- Select a waveform and adjust parameters. The GUI will send commands to the BK Precision device and display feedback.

# Controller Sync Logic
This script uses a signaling file (controller_ready.txt) to coordinate readiness across multiple controllers:
- Writes "BKP_Arb_Waveform_Controller is ready" to the file
- Waits for other controllers to report readiness
- Clears the file on exit
Expected controllers:
- Substrate Heater
- TPG261
- MKS Pressure
- Ircon Modline Plus  
  
To run independently (without the sync logic, comment or delete this code)  

```python
with open('controller_ready.txt', 'a') as f:
    f.write('BKP_Arb_Waveform_Controller is ready\n')
    
# waiting for all controllers to be ready
expected_controllers = ['Substrate_Heater_Controller', 'TPG261_Controller', 'MKS_Pressure_Controller', 'BKP_Arb_Waveform_Controller', 'Ircon_Modline_Plus_Controller']
ready = False

while not ready:
    with open('controller_ready.txt', 'r') as f:
        lines = f.readlines()
        
    ready = all(f'{controller} is ready\n' in lines for controller in expected_controllers)
    
    if not ready:
        print('Waiting for all controllers to be ready')
        time.sleep(0.01)
```

# File Structure
BK_Arb_Waveform_GUI
- cont_BK_Arb_Waveform_Generator_V3.py
- mod_BKP_4054B.py
- controller_ready.txt
- README.md
- manuals
    - BK_4050B_Series_Dual_Channel_FunctionArbitrary_Waveform_Generators_Datasheet.pdf
    - BK_4050B_Series_Dual_Channel_FunctionArbitrary_Waveform_Generators_Manual.pdf
    - BK_4050B_Series_Dual_Channel_FunctionArbitrary_Waveform_Generators_Programming_Manual.pdf



# Manuals
This repo includes the manuals for the waveform generator and usage documentation. 

# Notes for Developers
- GUI layout is modular and extensible
- Parameters are bound to tk.DoubleVar for real-time updates
- Read-only fields reflect live instrument state
- Easily adaptable for other waveform generators or lab instruments
