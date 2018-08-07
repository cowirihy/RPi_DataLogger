# -*- coding: utf-8 -*-
"""
Main data logging script
Runs parallel threads to systematically acquire and pre-process data

Created on Tue Jun 19 16:03:12 2018
@author: ARIR
"""

import threading
import time

# Define classes used in core threads
import ticker
import acquisition
import pre_processor
import watchdog

import get_data_funcs as dataGetFunc
from get_data_funcs import RTIMU

#%% Start of main script

# Define IMU (to be used to acquire data)
s = RTIMU.Settings('RTIMU_settings')
imu = RTIMU.RTIMU(s) 

if (not imu.IMUInit()): 
    print("IMU:\tInitialisation failed\n\tUsing emulated IMU")
    fake_IMU = True
    
else: 
    print("IMU:\tInitialisation successful\n\tIMU Name:\t%s" % imu.IMUName())
    fake_IMU = False

# Define sampling functions for each channel
reader = dataGetFunc.AccelReader(imu, fake_IMU)
    
samplingFunctions = [lambda :reader.x_accel_take(fetch_new_data = True), 
                     lambda :reader.y_accel_take(),
                     lambda :reader.z_accel_take()] 

# **** KEY PARAMETERS CONTROLLING DATA ACQUSITION ****
file_length = 5.0                  # in seconds
fs = 16                             # sampling frequency (Hz)
timeOut = 30.0                      # timeout duration (secs)

dt = 1/fs                            # sampling period (secs)
maxCacheSize = file_length * fs     # number of data rows per file


ch_names = ['ACCX','ACCY','ACCZ']

# Define pre-processor functions
def addition_1(xx):
    yy = xx + 1
    return yy
    
def subtract_1(xx):
    yy = xx - 1
    return yy

def do_nothing(xx):
    return xx

pre_process_func = [[do_nothing],[do_nothing],[do_nothing]]

# Creates events 
eventGoGetData = threading.Event()
eventFileReady = threading.Event() 
event_ticker_timeout = threading.Event()

# Create a Ticker instance
tick_obj = ticker.Ticker(tick_event=eventGoGetData,
                         dt=dt, timeout=timeOut,
                         tick_timeout_event=event_ticker_timeout)

# Creates an AcquisitionSystem instance
ASys = acquisition.AcquisitionSystem(sampling_funcs=samplingFunctions,
                                     maxRowsPerFile=maxCacheSize,
                                     channel_names=ch_names)

# Creates a PreProcessor instance
PrePross = pre_processor.PreProcessor(pre_process_func,
                                      channel_names=ch_names) 

# Create a Watchdog instance
Watchdog = watchdog.Watchdog(ASys,PrePross,event_ticker_timeout)

# Define threads
ticker_thread = threading.Thread(name= 'Ticker', 
                                 target = tick_obj.run)

Acq_thread = threading.Thread(name = 'Acquisition',
                              target = ASys.run,
                              args=(eventGoGetData, 
                                    eventFileReady, 
                                    event_ticker_timeout),
                              kwargs={'verbose':True})
                                                   
PreProcess_thread = threading.Thread(name = 'Pre-Processor',
                                     target = PrePross.run,
                                     args=(eventFileReady, 
                                           event_ticker_timeout),
                                     kwargs={'verbose':True})
                                     
Watchdog_thread = threading.Thread(name = 'Watchdog',
                                   target = Watchdog.run,
                                   kwargs={'verbose':False})                                     

# Start threads
Watchdog_thread.start()
time.sleep(1.0)
ticker_thread.start()
time.sleep(1.0)
Acq_thread.start()
time.sleep(1.0)
PreProcess_thread.start()





