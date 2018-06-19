# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:03:12 2018
@author: ARIR

Main Data Logger thread:
    Gets data with a sampling frequency of 10Hz, max file size of 50 lines, 
    with a timeout of 10s
    Currently only runs a ticker thread and acquisition 19/6/2018
"""
import numpy as np
import randomNum
from ticker_example import ticker
import threading
from datetime import datetime
#%% start of main code

#### Inputs
samplingFunctions = [randomNum.randomNum, randomNum.randomNum] 
maxCacheSize = 50.0 
fs = 10.0; T = 1/fs
timeOut = 10.0

#Creates an AcquisitionSystem 
ASys = AcquisitionSystem(samplingFunctions)

#Creates events
eventGoGetData = threading.Event()
eventFileReady = threading.Event() #Does not yet do anything


#Define and start threads
ticker_thread = threading.Thread(name= 'ticker', 
                                 target = ticker, 
                                 args = (eventGoGetData,), 
                                 kwargs = {'timeout':timeOut, 'T':T})

Acq_thread = threading.Thread(name = 'Acquisition',
                               target = runAcquisition,
                               args=(eventGoGetData, eventFileReady, ASys,),
                               kwargs={'maxCacheSize':maxCacheSize})

ticker_thread.start()
Acq_thread.start()

