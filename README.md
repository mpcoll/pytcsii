# pytcsii: A python package to interface with the QST.Lab TCS II thermal stimulator


![TCSII]([https://assets.digitalocean.com/articles/alligator/boo.svg](https://static.wixstatic.com/media/cdfa5d_c7427cb0e2d649c79ebf5fcbcb69d052~mv2_d_2998_2248_s_2.png/v1/fill/w_2998,h_2245,al_c,q_95,enc_auto/cdfa5d_c7427cb0e2d649c79ebf5fcbcb69d052~mv2_d_2998_2248_s_2.png)


> :warning: This package has not been extensively tested. Use at your own risk. Verify that the serial commands sent to the device are giving the expected results and double-check the generated protocol files before using them on the device. Please report any issues you may encounter.




## Installation

pip install git+https://github.com/mpcoll/pytcsii.git


## Usage

### Serial control

When the TSC II stimulator is in computer control mode (connected to a computer, powered on, no image on the device monitor), the *tscii_serial* module can be used to easily send serial commands to the stimulator.

Example usage:

```python
from pytscii import tcsii_serial

port_address = 'COM3' # Address of the TSC II virtual serial port
 
tcsii = tcsii_serial(port_address) # Initialize
tcsii.set_baseline(30) # Set baseline to 30
# Prepare to send a stimulation of 2 s at 45°C with rise/return rates of 20°C/s
# NOTE: See duration modes in the functions to set the duration correctly
tcsii.set_stim(target=45, rise_rate=20, return_rate=20, dur_ms=2000)

# Trigger the stimulation
tcsii.trigger()
```


### Protocol generator

The *tcsii_protocol_generator* module can be used to generate protocol files that can then be transferred to the device using a USB dongle and used in the "Custom protocols" screen.

Example usage for a simple protocol:
```python
from pytcsii import tcsii_protocol_generator

# Initialize and choose filename for output
protocol = tcsii_protocol_generator(filename='path/simple_protocol',
                                    generate_figure=True)

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

For longer protocols, the *generate_from_lists* function can be used to generate a list of stimulation trials interleaved with a wait option. If a fixed value is passed instead of a list, all trials will have the same value for this parameter. 

Example usage for a longer protocol:
```python
from pytcsii import tcsii_protocol_generator

# Initialize and choose the filename for the output
protocol = tcsii_protocol_generator(filename='path/long_protocol',
                                    generate_figure=True)

# Generate a list of 5 trials with a wait for trigger in between each trial
temp_trials = [45, 40, 42, 44, 42]

protocol.generate_from_lists(temp_list=temp_trials,
                             duration_smmm=2.000,
                             wait_type='trigger_in')
protocol.export()
```
