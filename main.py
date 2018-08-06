# -*- coding: utf-8 -*-
"""
Main data logging script
Runs parallel threads to systematically acquire and pre-process data

Created on Tue Jun 19 16:03:12 2018
@author: ARIR
"""

from ticker import ticker
import threading

# Define classes used in core threads
import acquisition as acqSys
import pre_processor as prePro

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
file_length = 3.0                   # in seconds
fs = 16                             # sampling frequency (Hz)
timeOut = 15.0                      # timeout duration (secs)

T = 1/fs                            # sampling period (secs)
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

# Creates an AcquisitionSystem instance
ASys = acqSys.AcquisitionSystem(sampling_funcs=samplingFunctions,
                                maxRowsPerFile=maxCacheSize,
                                channel_names=ch_names)

# Creates a PreProcessor instance
PrePross = prePro.PreProcessor(pre_process_func,
                               channel_names=ch_names) 

# Creates events 
eventGoGetData = threading.Event()
eventFileReady = threading.Event() 
event_ticker_timeout = threading.Event()

# Define threads
ticker_thread = threading.Thread(name= 'ticker', 
                                 target = ticker, 
                                 args = (eventGoGetData,), 
                                 kwargs = {'timeout':timeOut, 
                                           'T':T, 
                                           'tick_timeout':event_ticker_timeout})

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

# Start threads
ticker_thread.start()
Acq_thread.start()
PreProcess_thread.start()


