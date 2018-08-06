# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:03:12 2018
@author: ARIR

Main Data Logger thread:
    Gets data with a sampling frequency of 10Hz, max file size of 50 lines, 
    with a timeout of 10s
    Currently only runs a ticker thread and acquisition 19/6/2018
"""

from ticker_example import ticker
import threading

# Define classes used in core threads
import acquisition_system as acqSys
import pre_processor as prePro

#import RTIMU
import DataGetFunc2 as dataGetFunc
from DataGetFunc2 import RTIMU

#%% start of main code

# Define IMU to be used to acquire data
s = RTIMU.Settings('RTIMU_settings')
imu = RTIMU.RTIMU(s) 

if (not imu.IMUInit()): 
    print("IMU:\tInitialisation failed\n\tUsing emulated IMU")
    fake_IMU = True
    
else: 
    print("IMU:\tInitialisation successful\n\tIMU Name:\t%s" % imu.IMUName())
    fake_IMU = False



reader = dataGetFunc.AccelReader(imu, fake_IMU)
    
samplingFunctions = [lambda :reader.x_accel_take(fetch_new_data = True), 
                     lambda :reader.y_accel_take(),
                     lambda :reader.z_accel_take()] 

maxCacheSize = 50.0 
fs = 16; T = 1/fs
timeOut = 10.0
fig_length = 30


def addition_1(xx):
    yy = xx + 1
    return yy
    
def subtract_1(xx):
    yy = xx - 1
    return yy

def do_nothing(xx):
    return xx

pre_process_func = [[do_nothing],[do_nothing],[do_nothing]]

#Creates an AcquisitionSystem 
ASys = acqSys.AcquisitionSystem(samplingFunctions)

#Creates a PreProcessor
PrePross = prePro.PreProcessor(pre_process_func) 


#Creates events
eventGoGetData = threading.Event()
eventFileReady = threading.Event() 
event_ticker_timeout = threading.Event()

#Define and start threads
ticker_thread = threading.Thread(name= 'ticker', 
                                 target = ticker, 
                                 args = (eventGoGetData,), 
                                 kwargs = {'timeout':timeOut, 
                                           'T':T, 
                                           'tick_timeout':event_ticker_timeout})

Acq_thread = threading.Thread(name = 'Acquisition',
                              target = acqSys.runAcquisition,
                              args=(eventGoGetData, 
                                    eventFileReady, 
                                    ASys, 
                                    event_ticker_timeout),
                              kwargs={'maxCacheSize':maxCacheSize})
                               
PreProcess_thread = threading.Thread(name = 'Pre-Processor',
                                     target = PrePross.run,
                                     args=(eventFileReady, 
                                           event_ticker_timeout))


ticker_thread.start()
Acq_thread.start()
PreProcess_thread.start()


