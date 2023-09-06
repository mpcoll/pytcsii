import serial
import time
import matplotlib.pyplot as plt
import numpy as np

""" 
TCSII serial commands
Command list:
'H'.     : this help
'?'.     : returns 'TCS'
'Nxxx'.   : set neutral temperature in 1/10 degrees ('xxx'='200' to '400')
'G'.     : calibrate neutral temperature ( after few seconds return 'Nxxx' with xxx = neutral temperature in 1/10 degrees ) 
'Sxxxxx'  : enable/disable area 1 to 5 (x='1'=enable or '0'=disable)
'Csxxx'   : set stimulation temperature in 1/10 degrees ('s'='0'(all areas) or '1' to '5', 'xxx'='100' to '600')
'Vsxxxx'  : set stimulation speed in 1/10 degrees per seconds ('s'='0'(all areas) or '1' to '5', 'xxxx'='0001' to '9999')
'Rsxxxx'  : set return speed in 1/10 degrees per seconds ('s'='0'(all areas) or '1' to '5', 'xxxx'='0001' to '9999')
'Dsxxxxx' : set stimulation Duration in ms ('s'='0'(all areas) or '1' to '5', 'xxxxx'='00001' to '99999')
'Txxxyyy' : set Trigger number and duration (number 'xxx'='001' to '255', duration 'yyy'='010' to '999')
À

'P'.     : display stimulation Parameters (global and for each area)
'L'.     : start stimuLation
'A'.     : Abort current stimulation or exit 'follow mode', return to neutral
'F'.     : 'mute mode', disable display of temperatures between and during stimulations
'Yxxxx'   : set the duration of temperature display during stimulation in ten ms ('xxxx'='0000' to '9999')
...       if set to '0000' (default state) displays temperatures during the entire stimulation
'Oa'.     : enable temperatures display between stimulations ( 1Hz, active by default )
'Ob'.     : enable temperatures display during stimulations ( 100Hz, active by default )
'Oc'.     : reset stimulator
'Od'.     : 'follow mode': probe goes to the setpoint temperature and remains there as long as the setpoint does not change.
'Omxxx'   : Defines a maximum stimulation temperature ('xxx' 1/10 degrees). 'C' command is limited to this temperature.
'Ovsxxxxx': set stimulation speed in 1/100 degrees per seconds ('s'='0'(all areas) or '1' to '5', 'xxxxx'='00001' to '99999')
'Orsxxxxx': set return speed in 1/100 degrees per seconds ('s'='0'(all areas) or '1' to '5', 'xxxxx'='00001' to '99999')
'Otsxxxx' : set stimulation temperature in 1/100 degrees ('s'='0'(all areas) or '1' to '5', 'xxxx'='0001' to '6000')
'Oe'.     : display currEnt temperatures for neutral and area 1 to 5 in 1/100 degrees
'Osx'.   : enable (x='e') or disable (x='d') the launch of a stimulation using the trigger in
'Oo'.     : Output trigger
'B'.     : display Battery voltage and % of charge
'Ix'.     : enable/disable Integral term, 'x'='1' : enable(default state), 'x'='0' : disable
'E'.     : display currEnt temperatures for neutral and area 1 to 5 in 1/10 degrees
'K'.     : get 'stim' & 'resp' buttons state ( CR+'00':both released, CR+'11':both pressed, CR+'10':'stim' button pressed,...)
'Q'.     : get error state ( return 'xxxxxx', for each zone+neutral: 'x'=0:OK,'x'>1:ERROR )
'Ur'.     : display temperature profile for each area: area number(1..5), profile enabled, number of points defined, points list
'Uwxxxxxnnndddtttdddttt...' : User defined temperature profile, defined by segments of variable duration
... 'xxxxx': areas defined ('11111' all areas, '10000' just area 1, ...), 'nnn': number of segments ('000' to '999')
... 'dddttt': list of duration of segment in ten of ms ('001' to '999') and temperature at end of segment ('000' to '600')
'Uexxxxx' : enable/disable temperature profile for each area (x='1'=enable or '0'=disable=default)
'Xr'.     : clock read hour and date, return hhmmssddmmyy
'Xwhhmmssddmmyy' : clock write hour and date ( hh:heure, mm:minute, ss:seconds, dd:day, mm:month, yy:year )
'Zdddfff' : Buzzer ddd: duration in 10x ms, fff: frequency in 10x Hz
'OiI'.: program Irm room extension cable
'OiC'.: program Control room extension cable
'Oim'.: measure temperature of extension cable ( takes about 1.5s )
'Oit'.: display temperature of extension cable
'Ofx'  : set IRM filter strength, 'x'='1':low, 'x'='2':medium, 'x'='3':high 
'Ol'   : starts a stimulation which can be stopped by the response button 
'Og'   : display current temperatures and buttons state (merges 'E' and 'K' command).

"""



class tcsii():
    def __init__(self, port, baseline=30, surfaces=0, max_temp=50, beep=False, trigger_in=True):
        """Connect to TSCII and set baseline and max temperature

        Args:
            port (str): Serial port name
            baseline (int, optional): Baseline temperature. Defaults to 30.
            surfaces (int or list): Surfaces to use. 0 for all surfaces. Defaults to 0.
        """        
        self.baseline = baseline # Baseline temperature
        self.max_temp = max_temp # Maximum temperature

        if baseline > 45 or baseline < 30: # Check if baseline is in range
            Warning('Baseline temperature is out of 30-45 range')
        self.port = serial.Serial(port, baudrate=115200, timeout=0.1)  # Open port
        self.port.write(('N' + self.format_temp(baseline)).encode()) # Set baseline on all surfaces
        # Set max temperature
        self.port.write(('Om' + self.format_temp(self.max_temp)).encode()) # Set max temperature
        self.port.write('F'.encode()) # Stop constant data stream
        self.stim_set = False # Indicate that no stimulation parameters have been set.
        self.beep = beep # Beep on stim start
        self.trigger_in = trigger_in # Lauch on trigger in
        if self.trigger_in:
            self.port.write('Ose'.encode()) # Enable trigger in
        else:
            self.port.write('Osd'.encode()) # Disable trigger in

    def format_temp(self, temp, zero_fill_len=3):
        """Format temperature in 1/10 degrees

        Args:
            temp (int): temperature in degrees Celsius

        Returns:
            str: temperature in 1/10 degrees as a str
        """
        temp = str(temp*10).zfill(zero_fill_len)
        return temp

    def format_ms(self, ms, zero_fill_len=5):
        """Format ms with leading zeros

        Args:
            ms (int): duration in ms

        Returns:
            str: ms formatted with leading zeros
        """
        ms = str(ms).zfill(zero_fill_len)
        return ms
    

    
    def custom_command(self, command):
        """Send a custom command to TSCII

        Args:
            command (str): Valid command from TSCII manual
        """        
        self.port.write(command.encode())
    

    def reset(self):
        # Reset stimulator (turn off an on)
        print('Resetting stimulator')
        self.port.write('Oc'.encode()) # Reset stimulator

    def set_baseline(self, baseline):
        # Set baseline temperature
        if baseline > 45 or baseline < 30: # Check if baseline is in range
            Warning('Baseline temperature is out of 30-45 range')
        self.port.write(('N' + self.format_temp(baseline)).encode()) # Set baseline on all surfaces

    def print_temp(self):
        """Print current temperature"""        
        self.port.flush()
        self.port.write('E'.encode()) # Display current temperature
        print(self.port.read_until(str('\n').encode('utf-8')).decode()) # print temperature

    def set_stim(self, target, rise_rate, return_rate, dur_ms=None, dur_mode='fixed_stim', trigger_code=255, trigger_dur_ms=10,
                 surfaces=0):
        """Set the stimulation parameter for the TCSII

        Args:
            target (int): target temperature in C
            rise_rate (int): rise rate in C/s
            return_rate (int): return rate in C/s
            dur_ms (int):  duration in ms. Phases duration depends on dur_mode.
            dur_mode('string):
                'fix_stim' (rise + plateau are total time and return is 0) 
                'fixed_plateau' (duration is for plateau and rise/return rates are additional time) 
                'fixed_total' (duration is total time and rise/return rates are included)
                Defaults to fix_stim
            total_dur_ms (int) Total stim duration in ms (rise + plateau). Must be None if plateau_dur_ms is set.
            trigger_code (int, optional): trigger code. Defaults to 255.
            trigger_dur_ms (int, optional): trigger duration. Defaults to 10.
            beep (bool, optional): send beep on success. Defaults to False.
        """        

        # Store parameters
        self.stim_set = True
        self.stim_target_temp = target
        self.stim_rise_rate = rise_rate
        self.stim_return_rate = return_rate
        self.stim_trigger_code = trigger_code
        self.stim_strigger_dur_ms = trigger_dur_ms

        # Duration for rise
        self.stim_rise_dur_ms = int((self.stim_target_temp - self.baseline) / self.stim_rise_rate * 1000)
        self.stim_return_dur_ms = int((self.stim_target_temp - self.baseline) / self.stim_return_rate * 1000)

        # Total duration including plateau


        if dur_mode == 'fixed_plateau':
            dur_ms = dur_ms + self.stim_rise_dur_ms # Add rise time so that selected duration applies only to plateau
        if dur_mode == 'fixed_total':
           self.stim_duration_ms = dur_ms - self.stim_return_dur_ms # Remove return time so total includes return time
        if dur_mode == 'fixed_stim':
           self.stim_duration_ms = dur_ms # By default, duration is rise + plateau
        self.duration_mode = dur_mode
    

        # Send parameters to TSCII
        self.port.write(('C0' + self.format_temp(self.stim_target_temp)).encode()) # Set the target temp
        self.port.write(('V0' + self.format_temp(self.stim_rise_rate, zero_fill_len=4)).encode()) # Set the rise change rate
        self.port.write(('R0' + self.format_temp(self.stim_return_rate, zero_fill_len=4)).encode()) # Set the rise change rate
        self.port.write(('D0' + self.format_ms(self.stim_duration_ms, zero_fill_len=5)).encode()) # Set the rise change rate


        # Set surfaces
        self.surfaces = surfaces # Surface to use
        if type(surfaces) == list: # Check if all surfaces are used
            self.all_surfaces = False

        else:
            self.all_surfaces = True

        # SEt the surfauces
        if self.all_surfaces:
            surf_ls = '11111'

        else:
            surf_ls = ''
            for i in range(1, 6):
                surf_ls += '0' if i not in surfaces else '1'

        self.port.write(('S' + surf_ls).encode()) # Set the surfaces


    def trigger(self):
        self.port.write('L'.encode()) # Trigger stimulation
        # Beep if beep is set
        if self.beep:
              self.tport.write('Z010100'.encode())

    def trigger_and_save_temp(self, frequency=1000, offset_s=1):
        elapsed = 0
        all_outs = []
        if self.beep:
              self.tport.write('Z010100'.encode())

        self.port.write('L'.encode()) # Trigger stimulation

        # Read and print temperature at 100 Hz
        now = time.time()
        while elapsed < (self.stim_total_duration_ms/1000 + offset_s):
            self.port.write('E'.encode())
            out = self.port.readline().decode()
            all_outs.append(out)
            elapsed = time.time() - now

        # Format output
        all_outs = [i.replace('\r', '').replace('\n', '') for i in all_outs]
        outs = np.asarray([i.split('+') for i in all_outs]).astype(float)/10

        self.read_outs = outs


    def trigger_and_plot_temp(self, frequency=100, offset_s=1, fig_each_zone=False):
        elapsed = 0
        all_outs = []
        if self.beep:
              self.tport.write('Z010100'.encode())

        self.port.write('L'.encode()) # Trigger stimulation

        # Read and print temperature at 100 Hz
        now = time.time()
        while elapsed < (self.stim_total_duration_ms/1000 + offset_s):
            self.port.write('E'.encode())
            out = self.port.readline().decode()
            all_outs.append(out)
            elapsed = time.time() - now

        # Format output
        all_outs = [i.replace('\r', '').replace('\n', '') for i in all_outs]
        outs = np.asarray([i.split('+') for i in all_outs]).astype(float)/10

        self.read_outs = outs


        if not fig_each_zone:
            fig = plt.figure()
            plt.plot(outs[:, 0], label='Zone neutral', linestyle='--', color='black')
            plt.plot(outs[:, 1], label='Zone 1', linestyle='-.')
            plt.plot(outs[:, 2], label='Zone 2', linestyle=':')
            plt.plot(outs[:, 3], label='Zone 3', linestyle='-')
            plt.plot(outs[:, 4], label='Zone 4')
            plt.plot(outs[:, 5], label='Zone 5')
            plt.axhline(self.stim_target_temp, label='target', linestyle='--', color='red')
            plt.axhline(self.baseline, label='baseline', linestyle='--', color='green')
            plt.xlabel('Sample', fontsize=14)
            plt.ylabel('Temperature', fontsize=14)
            plt.tick_params(labelsize=12)
            plt.legend()
            self.last_fig = fig
        else:
            self.last_fig = []
            for i in range(outs.shape[1]):
                fig = plt.figure()
                plt.plot(outs[:, i], label='Zone ' + str(i), linestyle='--', color='black')
                plt.axhline(self.stim_target_temp, label='target', linestyle='--', color='red')
                plt.axhline(self.baseline, label='baseline', linestyle='--', color='green')
                plt.xlabel('Sample', fontsize=14)
                plt.ylabel('Temperature', fontsize=14)
                plt.tick_params(labelsize=12)
                plt.legend()
                self.last_fig.append(fig)


class tcsii_protocol_generator():
    def __init__(self, filename, recordTemperatures=1):
        """Connect to TSCII and set baseline and max temperature

        Args:
            port (str): Serial port name
            baseline (int, optional): Baseline temperature. Defaults to 30.
            surfaces (int or list): Surfaces to use. 0 for all surfaces. Defaults to 0.
        """        
        self.filename = filename
        self.n_steps = 0
        self.recordTemperatures=recordTemperatures
        self.protocol = ['[protocol]', 'stepsNumber=0', 'recordTemperatures=' + str(recordTemperatures), '']


    def add_stimulation(self, target_temp, rise_rate, return_rate, 
                        duration_smmm, baseline=30.0, wait=0.000,  zones=[1, 2, 3, 4, 5], 
                        trig_out_val=255, trig_out_dur=0.300, duration_mode='fixed_plateau'):

        """Add a stimulation step to the protocol."""

        # Duration mode
        # 0: 'fixed_plateau' (duration is for plateau and rise/return rates are additional time) DEFAULT
        # 1: 'fixed_total' (duration is total time and rise/return rates are included)
        # 2: 'fix_stim' (rise + plateau are total time and return is 0)

        rise_time = (target_temp - baseline) / rise_rate
        return_time = (target_temp - baseline) / return_rate
        if duration_mode == 'fixed_plateau':
            duration_smmm = duration_smmm + rise_time  # Add rise time so that selected duration applies only to plateau
        if duration_mode == 'fixed_total':
            duration_smmm = duration_smmm - return_time # Remove return time so total includes return time
        if duration_mode == 'stim_only':
            duration_smmm = duration_smmm # By default, duration is rise + plateau


        # Format number to strings with 3 decimals
        duration_smmm = f'{duration_smmm:.3f}'
        target_temp = f'{target_temp:.3f}'
        baseline = f'{baseline:.3f}'
        wait = f'{wait:.3f}'
        trig_out_dur = f'{trig_out_dur:.3f}'
        trig_out_val = str(trig_out_val)
        rise_rate = f'{rise_rate:.3f}'
        return_rate = f'{return_rate:.3f}'

        self.n_steps += 1
        curr_step = self.n_steps
        self.protocol.append('[step' + str(curr_step) + ']')
        self.protocol.append('stepType=0')
        self.protocol.append('stepTypeText=STIMULATE')
        self.protocol.append('')
        self.protocol.append('[step' + str(curr_step) + '_stimulation]')
        self.protocol.append('baseline=' + baseline)
        self.protocol.append('triggerVal=' + trig_out_val)
        self.protocol.append('triggerDur=' + trig_out_dur)
        self.protocol.append('')

        for z in [1, 2, 3, 4, 5]:
            self.protocol.append('[step' + str(curr_step) + '_zone' + str(z) + ']')
            if z in zones:
                self.protocol.append('enabled=1')
            else:
                self.protocol.append('enabled=0')
            self.protocol.append('duration=' + duration_smmm)
            self.protocol.append('wait=' + str(wait))
            self.protocol.append('temperature=' + target_temp)
            self.protocol.append('speed=' + rise_rate)
            self.protocol.append('return=' + return_rate)
            self.protocol.append('pointToPointEnabled=0')
            self.protocol.append('nbrPts=1')
            self.protocol.append('sec1=1.000')
            self.protocol.append('deg1=30.000')
            self.protocol.append('')


    def add_wait_trigger_in(self):
        """Add a wait trigger step to the protocol."""
        self.n_steps += 1
        curr_step = self.n_steps
        self.protocol.append('[step' + str(curr_step) + ']')
        self.protocol.append('stepType=2')
        self.protocol.append('stepTypeText=WAIT')
        self.protocol.append('typeWait=3')
        self.protocol.append('typeWaitText=WAIT_TRIGGER')
        self.protocol.append('number=1')
        self.protocol.append('')


    def set_baseline(self, baseline_temp=30.0, adjust_to_skin=0):
        """Add a set baseline step to the protocol."""
        baseline_temp = f'{baseline_temp:.3f}'
        self.n_steps += 1
        curr_step = self.n_steps
        self.protocol.append('[step' + str(curr_step) + ']')
        self.protocol.append('stepType=6')
        self.protocol.append('stepTypeText=BASELINE')
        self.protocol.append('baseline=' + baseline_temp)
        self.protocol.append('adjustToSkin=' + str(adjust_to_skin))
        self.protocol.append('')

    def set_constant_temp(self, constant_temp, duration_s, speed, zones):
        """Add a set constant temperature step to the protocol."""
        constant_temp = f'{constant_temp:.3f}'
        speed = f'{speed:.3f}'
        duration_s = f'{duration_s:.3f}'
        self.n_steps += 1
        curr_step = self.n_steps
        self.protocol.append('[step' + str(curr_step) + ']')
        self.protocol.append('stepType=8')
        self.protocol.append('stepTypeText=SET_CONST_TEMP')
        for z in range(1,6):
            self.protocol.append('constTemp' + str(z) +  '=' + constant_temp)
            self.protocol.append('constTempSpeed=' + str(z) + speed)
            if z in zones:
                self.protocol.append('enableConsTemp' + str(z) + '=1')
            else:
                self.protocol.append('enableConsTemp' + str(z) + '=0')
            self.protocol.append('ConstTempHold' + str(z) + '=' + duration_s)
        self.protocol.append('')


    def export_protocol(self):
        """Export protocol to file."""
        self.protocol[1] = 'stepsNumber=' + str(self.n_steps)
        with open(self.filename + ".protocol.ini", 'w') as f:
            for line in self.protocol:
                f.write(line + '\n')
        f.close()


    def generate_from_lists(self, temp_list, 
                                        duration_smmm, zones, 
                                        rise_rate, return_rate,
                                        baseline=30.0, wait=0.000,
                                        trig_out_val=255, trigger_out_dur=0.100,
                                        duration_mode='fixed_plateau', n_trials=None):
        """
        Generate trials from a list of trials. If a parameter is a single value, it will be applied to all trials.
        If a parameter is a list, it must have the same length as temp_list.
        If temp_list is a single value, the n_trials parameter must be specified as an integer.
        """        
        
        if type(temp_list) is not list:
            assert n_trials # If temp_list is a single value, n_trials must be specified
            temp_list = [temp_list]*n_trials
        if type(duration_smmm) is not list:
            duration_smmm = [duration_smmm] * len(temp_list)
        if type(zones[0]) is not list:
            zones = [zones] * len(temp_list)
        if type(rise_rate) is not list:
            rise_rate = [rise_rate] * len(temp_list)
        if type(return_rate) is not list:
            return_rate = [return_rate] * len(temp_list)
        if type(trig_out_val) is not list:
            trig_out_val = [trig_out_val] * len(temp_list)

        # TODO adjust durations
        for target, duration, rise, retur_, trig_val, zone in zip(temp_list, duration_smmm, rise_rate, return_rate, trig_out_val, zones):
            self.add_wait_trigger_in()
            self.add_stimulation(baseline=baseline, target_temp=target, rise_rate=rise, return_rate=retur_, 
                                 duration_smmm=duration, wait=wait,
                                 zones=zone, trig_out_val=trig_val, trig_out_dur=trigger_out_dur, duration_mode=duration_mode)

