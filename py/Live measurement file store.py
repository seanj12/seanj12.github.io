# Developed for EP403 by Marcin Lukasz Gradziel

import libm2k
from libm2kmu import M2KContextManager
import numpy as np
import matplotlib.pyplot as plt
from time import sleep


# channel to use (libm2k.CHANNEL_1 or libm2k.CHANNEL_2)
channel = libm2k.CHANNEL_1

# number of samples to capture
num_samples = 10_750

# the global sampling frequency determines the shortest possible 
# interval between samples.  Available values are limited!
desired_sampling_frequency = 10_000
# oversampling ratio gives 
# 1 means that all samples are returned, 
# 2 that every second one is used (rest are discarded)
oversampling_ratio = 1
# this means that the effective sampling frequency is
# given by:
effective_sampling_frequency = desired_sampling_frequency / oversampling_ratio

# expected minimum value, can be conservative!
desired_minimum_voltage = -15.0
# expected maximum value, can be conservative!
desired_maximum_voltage = 15.0

# if this flag is on, the device will be programmed to use offset range
use_range_offset_function = False
if use_range_offset_function:
    midpoint = (desired_maximum_voltage + desired_minimum_voltage) / 2.0
else:
    midpoint = 0.0 # do not use level pre-shifting
class Constant:
    def __init__(self, value = False):
        self._value = value
    
    def __call__(self, time):
        return np.full_like(time, self._value)

class Pulses:
    def __init__(self,*, N = 1, F=1, DC = 0.5, delay = 0.0):
        self._N = N
        self._T = 1.0 / F
        self._DC = DC
        self._delay = delay
    
    def __call__(self, time):
        pulse_number = (time - self._delay) // self._T
        pulse_fraction = ((time - self._delay) % self._T) / self._T
        
        return (pulse_number >= 0) & (pulse_number < self._N) & (pulse_fraction <= self._DC)

# set overall generation window time is seconds

OVERALL_TIME = 1.2
SAMPLE_RATE = 10_000
BITS_USED = 6

# entries in this list declare individual bits as inputs (False) or outputs (True)
# 16 entries altogether
USE_AS_OUTPUT = [True, True, True, True, True, True, True, True,
                 True, False, False, False, False, False, False, False ]
          
# signals to use for various bits:
# None means ignore (False) -- appropriate for inputs
# Constant(True) -- signal that is always 1
# Constant(False) -- signal that is always 0
# Pulses(N, F, DC, DELAY) -- after a delay of DELAY, represent N pulses at
# frequency F and duty cycle DC

SIGNALS = [ Pulses(delay=0.025,N=21,F=20,DC=0.5),
          Pulses(delay=0.05,N=11,F=10,DC=0.5),
          Pulses(delay=0.1,N=5,F=5,DC=0.5),
          Pulses(delay=0.2,N=3,F=2.5,DC=0.5),
          Pulses(delay=0.4,N=3,F=1.25,DC=0.5),
          Pulses(delay=0.8,N=1,F=0.625,DC=0.5),
          Constant(True),
          Constant(True),
          Pulses(delay=1e-4,N=1,F=1000,DC=0.5),
          None,None,None,None,None,None,None]
    # Constant(True), Pulses(N=50,F=10_000,DC=0.5), None, None, None, None, None, None, 
    #        None, None, None, None, None, None, None, None]

# __Important note__
# 
# All of the ADALM2000 code should be within this with statement
# this ensures that the context is correctly deallocated even in the
# case of an error, an exception or explicit user interrruption.
# Without this (pun intended) Python would have to be restarted to allow 
# reuse of the hardware.

with M2KContextManager() as ctx:    
    
    dig=ctx.getDigital()
    dig.reset()
    
    # set the digital output sample rate
    dig.setSampleRateOut(SAMPLE_RATE)    
    
    #  configure all the digital pins
    for i, output_bit in enumerate(USE_AS_OUTPUT):
        if output_bit:
            dig.setDirection(i,libm2k.DIO_OUTPUT)
        else:
            dig.setDirection(i,libm2k.DIO_INPUT)
            
        dig.enableChannel(i,True)
    
    sample_rate = dig.getSampleRateOut()
    sample_period = 1.0 / sample_rate
    
    # determine the number of samples that will be output
    num_samples = int(OVERALL_TIME / sample_period) + 1
    
    print(f'Digital output sample rate is {sample_rate}.')
    print(f'{num_samples} samples will be output once.')
    # determine the time offsets of individual samples
    sample_times = np.arange(num_samples) * sample_period + 0.5/SAMPLE_RATE
    
    # all the samples, all zero for now
    samples = np.zeros(num_samples, dtype='int16')
    for i, signal in enumerate(SIGNALS):
        if signal:
            # get the signal values at all sample times
            pin_samples = signal(sample_times)
            # convert to 0 or 1 (int), multiply by the pbit weight
            # and add to the overall signal (all pins)
            samples += 2**i * pin_samples.astype(int)
            
    # output only once !
    dig.setCyclic(True)
    dig.push(samples.data)
    ain=ctx.getAnalogIn()
    ain.reset()
    ctx.calibrateADC()
        
    ain.enableChannel(channel,True)
    ain.setSampleRate(desired_sampling_frequency)
    ain.setOversamplingRatio(oversampling_ratio)
    
    # ADALM2000 has a trick up its sleeve, despite only two input gains!
    # it can offset input voltages by a programmable amount, before digitising
    # This means that the more sensitive range can be used on voltages 
    # in excess of +/- 2.5 V, as long as the range of expected values is
    # narrow enough
    # try to set that up if requested
    if use_range_offset_function:
        ain.setVerticalOffset(channel,-midpoint)
        
    ain.setRange(channel,desired_minimum_voltage - midpoint,
                 desired_maximum_voltage - midpoint)
    
    trigger = ain.getTrigger()
    trigger.setAnalogMode(channel, libm2k.EXTERNAL)
    
    # the offset range mode seems to come with a notable settling time,
    # that can affect the start of the first high sampling rate captures
    # avoid this by adding a short delay
    if use_range_offset_function:
        sleep(0.05)
    print(f'Wanted {desired_minimum_voltage} to {desired_maximum_voltage} V range')
    
    # determine what we were able to get
    gain, (low_limit, high_limit) = ain.getAvailableRanges()[ain.getRange(channel)]
    offset = - ain.getVerticalOffset(channel)
    
    print(f'Got {low_limit + offset} to {high_limit +offset} V effective range ( {gain} gain setting)')
    
    print()
    
    print(f'Wanted {effective_sampling_frequency} S/s sampling rate')
    actual_sampling_frequency = ain.getSampleRate()/ain.getOversamplingRatio()
    print(f'Got {actual_sampling_frequency} S/s sampling rate')
    
    if actual_sampling_frequency != desired_sampling_frequency:
        print('Available sampling frequencies are: ', ain.getAvailableSampleRates())
    
    # set up the figure and individual plots
    # then make it interactive
    fig, axs = plt.subplots(1, 1)
    fig.set_dpi(150)
    
    plt.ion()

    first_time = True
    i=0
    while True:    
        samples = np.asarray(ain.getSamples(num_samples)[channel]) # both are always measured!
        times = np.arange(len(samples)) / actual_sampling_frequency
        n = len(samples)
        channel_values=[]
        start_index=134+25
        while start_index < n-200:
            channel_values.append(samples[start_index:start_index+200].mean())
            start_index += 250
        timestep = 1.0 / actual_sampling_frequency
        freqs = np.fft.rfftfreq(n, d=timestep)
        if first_time:
            # create the plots from scratch in the first paSS
            axs.set_xlabel('channel')
            axs.set_ylabel('amp [V]')
            #axs[1].set_xlabel('f [Hz]')
            #axs[1].set_ylabel('amp [dBV]')
            time_plot, = axs.plot(times/0.025, samples,'.')
            channel_numbers=np.arange(0,len(channel_values))
            channel_plot, =axs.plot(channel_numbers, channel_values, '.r')
            plt.grid(visible=True, which='both', axis='both')
            #freq_plot, = axs[1].plot(freqs,20.0 * np.log10(np.abs(spectrum)),'.')
            plt.tight_layout()
            first_time = False
        else:
            # now only update the data. Do not create new plots!
            time_plot.set_xdata(times/0.025)
            time_plot.set_ydata(samples)
            channel_plot.set_ydata(channel_values)
           # freq_plot.set_xdata(freqs)
            #freq_plot.set_ydata(20.0 * np.log10(np.abs(spectrum)))
            # rescale the plots for potentially new data
            axs.relim()
            axs.autoscale_view(True, True, True)
            #'axs[1].relim()
            #axs[1].autoscale_view(True, True, True)
        
        # allow the interactive figure canvas to redraw regularly
        fig.canvas.draw()
        fig.canvas.flush_events()
        
        #np.savetxt(f"samples{i}.csv", np.asarray(samples).T)
        
       

