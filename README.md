# pytscii: A python package to interface with the QST.Lab TCS II thermal stimulator


## Installation

pip install git+https://github.com/mpcoll/pytcsii.git


## Usage

### Serial control

When the TSC II stimulator is in computer control mode (connected to a computer, powered on, no image on the device monitor), the tscii_serial class can be used to easily send serial commands to the stimulator.

Example usage:

```python
from pytscii import tscii_serial

port_address = 'COM3' # Adress of the TSC II virtual serial port
 
tcsii = tscii_serial(port_address) # Initialize
tcsii.set_baseline(30) # Set baseline to 30
# Prepare to send a stimulation of 2 s at 45°C with rise/return rates of 20°C/s
# NOTE: See duration modes in the functions to set the duration correctly
tcsii.set_stim(target=45, rise_rate=20, return_rate=20, dur_ms=2000)

# Trigger the stimulation
tcsii.trigger()
```


### Protocol generator

This function can be used to generate protocol files that can then be transferred to the devise using a USB dongle and used in the "Custom protocols" screen.

Example usage for a simple protocol:
```python
from pytscii import tcsii_protocol_generator

# Initialize and choose filename for output
protocol = tcsii_protocol_generator(filename='path/simple_protocol')

# Set baseline
protocol.set_baseline(baseline_temp=30.0)

# Add a wait trigger in
protocol.add_wait_trigger()

# Add a stimulation of 2 s at 45°C with rise/return rates of 20°C/s
protocol.add_stimulation(target_temp=45.0, rise_rate=20.0, return_rate=20.0, 
                        duration_smmm=2.000]
    
# Generate the protocol file
# The FILENAME.protocol.ini file generated can then be loaded on the device
protocol.export()
```

Example usage for a longer protocol:
```python
from pytscii import tcsii_protocol_generator

# Initialize and choose filename for output
protocol = tcsii_protocol_generator(filename='path/long_protocol')

temp_trials = [45, 40, 42, 44, 42]
dur_trials = [2.0, 1.0, 3.0, 4.0]

# The generate_from_lists function can be used to generate a list of trials intersped by a a wait option.



```
