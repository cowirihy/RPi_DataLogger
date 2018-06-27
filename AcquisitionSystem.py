# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 10:39:43 2018

@author: ARIR
"""
from datetime import datetime
import numpy as np
import os

class AcquisitionSystem:
    """
    Creates an Acquisition System with a certain number of channels.
    
    Inputs:  dataSampleFunc - a list of function handles, each one a way of 
    getting data for each required channel.
    """
    
    
    def __init__(self, dataSampleFunc):
        """
        Initilises the number of channels inputed by measuring the number of 
        elements of dataSampleFunc (a list of functions, each one a way of 
        getting data - one for each different channel).
        """
        self.sampleFunc = dataSampleFunc
        self.numChannels = len(self.sampleFunc)
        self.foundData = [None]*(self.numChannels + 1) # add one column for the time
        self.channels = {}
        for channelNum in range(0,self.numChannels):
            self.channels[channelNum] = Channel(channelNum, dataSampleFunc[channelNum])
    
    def createFile(self):
        """
        Creates a new file with the date and time in UTC time. 
        ~ Stores the file name in fileName for other methods to use as the 
        'current file'.
        ~ Adds a header file with the file name and column headers to the start 
        of the file.
        ~ Resets the numInFile variable to zero to represent no lines of data 
        yet in file. 
        """
        
        self.fileName = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".csv"
        currentFile = open(self.fileName,'a')
        
        # Write the headers
        headerLine1 = [self.fileName] + ['']*self.numChannels
        headerLine2 = ['Timestamp']
        for channelNum in range(0, self.numChannels):
            headerLine2 = headerLine2 + ['Ch' + str(channelNum) ]
        write_line(currentFile,
                   list_to_string(headerLine1, 
                                  delimiter=','))
        write_line(currentFile,
                   list_to_string(headerLine2, 
                                  delimiter=','))
        
        # Reset amount of data in file
        self.numInFile = 0
    
    def saveData(self):
        """
        Saves the current data to the current file. Adds one to the numInFile 
        variable, representing a line added to the file
        """
        currentFile = open(self.fileName,'a')
        write_line(currentFile,list_to_string(self.foundData, delimiter=','))
        currentFile.close()
        self.numInFile += 1
    
    def getDataAllChannels(self):
        """
        ~ Able to get data from all channels "simultaneously" (not truely but 
        close enough) and place in a list. Can store 1 peice of data from each 
        channel at one time only.
        ~ Places the time of acquisition as a string in UTC time as the first 
        element in the list
        """
        
        for channelNum in range(0, self.numChannels):
            self.foundData[channelNum + 1] = self.channels[channelNum].getData()
        self.foundData[0] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    
    def file_Complete(self):
        
        old_name = self.fileName
        new_name = old_name[:-4] + '_Completed.csv'
        os.rename(old_name,new_name)
    
class Channel:
    """
    Creates a channel that can aquire data through a function handed to it. 
    Also has space to save its own channel number in an acquasition system.
    
    Inputs: dataSAmpleFunc - a way of 'getting data'.
            ownChannelNum (optional) - way of storing a channelNum
    """
    def __init__(self, ownChannelNum, dataSampleFunc):
        self.sampleFunc = dataSampleFunc
        self.channelNum = ownChannelNum

    def getData(self):
        """
        returns data acquired using the function handed to it in smapleFunc
        """
        return np.array(self.sampleFunc())    

#%% Main loops for getting data from the channels

def runAcquisition(tick_obj, 
                   fileReady_obj, 
                   AcqSys,
                   tick_timeout,
                   maxCacheSize:float=20):
    """
    Start an acquisitionSystem object AcqSys and creates a new file for this 
    to store data in. After an event (tick_obj) the system takes and saves a 
    sample from all channels in the system. This repeats untill the created 
    file reaches the maxCacheSize and starts a new one also triggering the 
    event fileReady_obj. If the event tick_obj times out (becomes unset) the 
    method ends.   
    """
    
    while not tick_timeout.isSet():
        AcqSys.createFile()
        
        while (AcqSys.numInFile < maxCacheSize) and (not tick_timeout.isSet()):
    
            tick_obj.wait()
            tick_obj.clear()
            
            AcqSys.getDataAllChannels()
            AcqSys.saveData()
        
        AcqSys.file_Complete()
        fileReady_obj.set()
        
        print("Acqusition System: File completed")
    print('Acqusition System: Finished')
    
def list_to_string(myList,delimiter=','):
    return delimiter.join(map(str, myList))

def write_line(file,str_line):
    file.write(str_line + '\n')