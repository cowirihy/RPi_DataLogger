# -*- coding: utf-8 -*-
"""
Classes used to control data acquisiton

@author: ARIR
"""
from datetime import datetime
import numpy as np
import os
import time

class AcquisitionSystem:
    """
    Class for acquiring data from channels
    """
    
    def __init__(self,
                 sampling_funcs, 
                 channel_names=None,
                 maxRowsPerFile:int=50,
                 verbose=True):
        """
        Initialises acquisition system
        
        ***
        Required:
            
        * `sampling_funcs`, _list_ of functions defining the sampling function 
          to be used to acquire data for each channel
          
        ***
        Optional:
            
        * `channel_names`, _list_ of _strings_, defining names of each channel
          
        """
        
        nChannels = len(sampling_funcs)
        
        # Define default names for channels
        if channel_names is None:
            channel_names = ["Ch%d" % x for x in range(nChannels)]
        
        # Define channels as dict of channel objects
        self.channels = []
        """
        List of channel objects
        """
        
        self.nChannels = 0
        """
        Number of channels defined
        """
        
        for i in range(nChannels):
            
            obj = Channel(index=i,
                          name=channel_names[i],
                          sampling_func = sampling_funcs[i])
            
            self.add_channel(obj)
            
            
        # Initialise data
        nChannels = self.nChannels
        self.foundData = [None]*(nChannels + 1) # add one column for the time
        """
        _List_, used as container for acquired data and timestamp
        """
        
        self.nRows = 0
        """
        _Integer_, denotes number of data rows written to current file
        """
        
        
        self.maxRows = maxRowsPerFile
        """
        _Integer_, denotes number of data rows to be written to each file
        (before file can be marked as complete)
        """
        
        if verbose:
            print("ACQ:\tAcquisition system initialised\n" + 
                  "\tChannels:\n\t{0}\n".format([x.name
                                                 for x in self.channels]) + 
                  "\tnChannels:\t%d\n" % self.nChannels + 
                  "\tmaxRows:\t%d" % self.maxRows)
    
        self.running = False
        """
        _Boolean_, True within run() method
        """
        
        self.missing_data_count = 0
        """
        _Integer_ counter to denote number of missing data lines in file
        currently being written
        """
        
        self.max_acq_time = 0.0
        """
        _Float_, denotes maximum time taken (secs) for any data acquisition loop
        for last file being written
        """
            
    
    def add_channel(self,channel_obj):
        """
        Adds a new channel to acquisition system
        """
        
        self.channels.append(channel_obj)
        self.nChannels += 1
        
        
    def has_missing_data(self):
        """
        Returns True if file contains missing data rows
        False otherwise
        """
        if self.missing_data_count>0:
            return True
        else:
            return False
        
    
    def create_file(self,file_prefix='data_raw/'):
        """
        Creates a new file with the date and time in UTC time. 
        ~ Stores the file name in fileName for other methods to use as the 
        'current file'.
        ~ Adds a header file with the file name and column headers to the start 
        of the file.
        ~ Resets the numInFile variable to zero to represent no lines of data 
        yet in file. 
        """
        
        # Define filename according to current time
        file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".csv"
        file_name = file_prefix + file_name
        self.fileName = file_name
        
        currentFile = open(self.fileName,'a')
        
        # Write the headers
        headerLine1 = [self.fileName] + [''] * self.nChannels
        
        headerLine2 = ['Timestamp']
        headerLine2 += [ch.name for ch in self.channels]
            
        write_line(currentFile,
                   list_to_string(headerLine1, 
                                  delimiter=','))
        write_line(currentFile,
                   list_to_string(headerLine2, 
                                  delimiter=','))
        
        # Reset amount of data in file
        self.nRows = 0
        
    
    def save_data(self):
        """
        Saves the current data by writing new row to the current file
        """
        currentFile = open(self.fileName,'a')
        write_line(currentFile,list_to_string(self.foundData, delimiter=','))
        currentFile.close()
        self.nRows += 1
        
        
    def get_proportion_complete(self):
        """
        Returns the proportion of lines complete, for file currently being written
        """
        return self.nRows / self.maxRows
        
    
    def get_data(self):
        """
        ~ Able to get data from all channels "simultaneously" (not truely but 
        close enough) and place in a list. Can store 1 peice of data from each 
        channel at one time only.
        ~ Places the time of acquisition as a string in UTC time as the first 
        element in the list
        """
        
        # Get timestamp
        self.foundData[0] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        
        # Get data from all channels
        for ch in range(self.nChannels):
            
            val = self.channels[ch].get_data()
            self.foundData[ch+1] = val
            
            if val is None:
                print('ACQ:\tWarning: failed to get data')
                self.missing_data_count += 1
            
    
    def file_complete(self,suffix:str='_Completed.csv',verbose=False):
        """
        Mark file as complete by renaming
        """        
        
        old_name = self.fileName
        new_name = old_name[:-4] + suffix
        os.rename(old_name,new_name)
        
        if verbose:
            print("ACQ:\tFile completed\n\t%s" % new_name)
            
        self.missing_data_count = 0 # reset counter
        self.max_acq_time = 0.0 # re-initialise
        
        
    def run(self,tick_obj, file_ready_obj, tick_timeout, verbose=True):
        """
        Starts data acquisition
        
        ***
        Required:
            
        * `tick_obj`, _event_ used to trigger data acquisition
        
        * `file_ready_obj`, _event_ used to flag (to other threads) when data 
          is avaliable (e.g. for pre-processing)
        
        * `tick_timeout`, _event_; when this becomes unset (denotes timeout) 
          this method ends
        
        """
        
        print("ACQ:\tThread started")
        self.running = True
        
        while not tick_timeout.isSet():
            
            self.create_file()
            
            last_time = time.time() # initialise
                        
            while self.nRows < self.maxRows:
                
                acq_time = time.time() - last_time
                    
                if acq_time > self.max_acq_time:
                    self.max_acq_time = acq_time

                tick_obj.wait()
                
                last_time = time.time() # denotes time at start of acq loop
                
                tick_obj.clear()
                
                self.get_data()
                self.save_data()
            
            self.file_complete(verbose=verbose)
            file_ready_obj.set()
            
        print('ACQ:\tThread finished')
        self.running = False
            
    
    
class Channel:
    """
    Class defining data acquisition channel
    """
    
    def __init__(self, index:int, sampling_func:callable, name:str,
                 units:str=""):
        """
        Initialisation method
        
        ***
        Required:
        
        * `index`, _integer_ to denote channel index
        
        * `name`, _string_ used to describe channel
        
        * `sampling_func`, _function_ used to acquire data for channel
        
        ***
        Optional:
            
        * `units`, _string_ used to describe units of channel data
        
        """
            
        self.sampling_func = sampling_func
        self.index = index
        self.name = name
        self.units = units


    def get_data(self):
        """
        Returns data acquired using the sampling function defined
        """
        data = self.sampling_func()
        data = np.array(data)
        return data  

#%% Helper functions    
    
def list_to_string(myList,delimiter=','):
    return delimiter.join(map(str, myList))

def write_line(file,str_line):
    file.write(str_line + '\n')