# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:03:12 2018
@author: ARIR

Main Data Logger thread:
    Gets data with a sampling frequency of 10Hz, max file size of 50 lines, 
    with a timeout of 10s
    Currently only runs a ticker thread and acquisition 19/6/2018
"""
import randomNum
from ticker_example import ticker
import threading
import acquisitionSystem as acqSys
import pre_processor as prePro

#%% start of main code

#### Inputs
samplingFunctions = [randomNum.randomNum, randomNum.randomNum] 
maxCacheSize = 1000.0 
fs = 100.0; T = 1/fs
timeOut = 60.0

def addition_1(xx):
    yy = xx + 1
    return yy
    
def subtract_1(xx):
    yy = xx - 1
    return yy


pre_process_func = [[addition_1,addition_1,addition_1],[subtract_1]]
layover_size = 20

#Creates an AcquisitionSystem 
ASys = acqSys.AcquisitionSystem(samplingFunctions)

#Creates a PreProcessor
PrePross = prePro.PreProcessor(pre_process_func, layover_size=layover_size)

#Creates events
eventGoGetData = threading.Event()
eventFileReady = threading.Event() #Does not yet do anything
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
                                     target = prePro.run_pre_processor,
                                     args=(PrePross,
                                           eventFileReady, 
                                           event_ticker_timeout))


ticker_thread.start()
Acq_thread.start()
PreProcess_thread.start()


