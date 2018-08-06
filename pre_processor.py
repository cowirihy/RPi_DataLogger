# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:15:21 2018

@author: ARIR
"""

import os
import numpy as np
import pandas as pd
import time

#%%

def default_load(file_name):
    """
    The default loading method: Assumes 1 line of header with the first column taken as the index.
    It takes None strings as a numpy nan object - important for the rest of the code to run robustly.
    """
    
    data = pd.read_csv(file_name, header = 1, index_col = 0)
    
    timestamps = np.array(data.index)
    data = np.array(data.replace('None',np.nan))

    return (timestamps, data)


def default_save(file_name, timestamps, data, col_titles):
    
    saved_data = pd.DataFrame(data, index=timestamps)
    saved_data.index.name = 'Timestamp'
    saved_data.to_csv(file_name, header=col_titles, mode='a')

#%%

class PreProcessor():
    
    def __init__(self,process_funcs,   
                 load_data_func=default_load,   
                 save_data_func=default_save,
                 delete_raw=False,
                 channel_names=None,
                 layover_size=20,    
                 input_folder='data_raw/',
                 output_folder='data_preprocessed/',   
                 keyword='Completed'): 

        
        self.data = np.array(None)
        """
        Data for all channels
        """
        
        self.process_funcs = process_funcs
        """
        List of pre-processing functions to apply to all channels
        """
    
        self.input_folder = input_folder
        """
        _String_ denoting relative path to folder containing raw data files 
        to be processed
        """
        
        self.output_folder = output_folder
        """
        _String_ denoting relative path to folder to contain data files once 
        processed
        """
        
        self.keyword = keyword        
        """
        Keyword used to select filter files requiring processing
        """
               
        self.first_run = True
        """
        _Boolean_, denotes first run of pre-processor
        """
        
        self.load_data_func = load_data_func 
        """
        Function used to load raw data from files
        """
        
        self.save_data_func = save_data_func
        """
        Function used to save processed data to files
        """
        
        self.delete_raw = delete_raw
        """
        _Boolean_, used to denote whether raw data files should be deleted 
        following pre-processing
        """
        
        self.layover_size = layover_size
        self.layover_data = np.empty((len(self.process_funcs), layover_size))
        """
        Data from previous file, required for some processing operations 
        (e.g. filtering)
        """
        
        self.max_channel_num = len(self.process_funcs)
        """
        Number of channels defined
        """
                
        if channel_names is None:
            channel_names = ['Ch %d' % x for x in range(len(self.process_funcs))]
        
        self.channel_names = channel_names
        """
        Strings to denote channels
        """
        
        self.file_index = self.init_file_index()
        """
        _Integer_ index denoting index of next raw data file to be processed.
        Typically 0, except when raw files are not being deleted
        or if raw files exist prior to initialisation of pre-processor
        """
        
        # Define attributes not initialised
        self.files_to_process = []
        """
        List of raw data files requiring pre-processing
        """
        
        self.processed_data = np.empty((0,self.max_channel_num))
        """
        Array of processed data
        """
        
        self.current_file = ""
        """
        _String_ denoting file currently being pre-processed
        """
        

    def init_file_index(self):
        """
        Initialises file index by counting number of data files already
        present in raw files folder at initialisation of the pre-processor
        
        (These files are not to be pre-processed)
        """
        
        self.file_index = 0
        self.check_files()
        return len(self.files_to_process)

    
    def check_files(self,verbose=False):
        """
        Obtains list of raw data files requiring pre-processing
        
        Returns:
            
        _Boolean_, True is file avaliable for processing
        """
            
        fldr = self.input_folder
        fnames = os.listdir(fldr)
        
        files_to_process = [fldr + s for s in fnames if self.keyword in s]
        
        self.files_to_process = files_to_process
        
        if verbose:
            print("Files avaliable:\n{0}".format(files_to_process))
        
        nFiles = len(files_to_process)
        
        if nFiles > 0 and self.file_index < nFiles:
            # Requested file in range
            return True
        
        else:
            return False
        
        
    def process_data(self):
        """
        Process the data using the functions defined
        
        Different processes can be applied in series and different processes 
        can be applied to different channels. Due to the layover data different 
        code runs dependant on it being the first, last or middling runs. Also 
        if it is the first, last or 
        further code runs if a file is the first and last to allow    
        """
        for channel_num in range(0,self.max_channel_num):
            raw_processed_data = self.data[:,channel_num]
            for process_num in range(0,len(self.process_funcs[channel_num])):
                
                if self.first_run == True:
                    # First file so no layover data can be added or deleted.
                    raw_processed_data = self.process_funcs[
                            channel_num][process_num](raw_processed_data)
                
                else:
                    if (process_num >= len(self.process_funcs[channel_num]) - 1) and (process_num == 0):
                        # If only one function being applied need to add and 
                        # remove layover data.
                        raw_processed_data = self.process_funcs[channel_num][
                            process_num](np.concatenate(
                                    (self.layover_data[channel_num,:], 
                                         raw_processed_data), axis=0))
                        raw_processed_data = raw_processed_data[
                                        self.layover_size:]
                    
                    elif process_num >= len(self.process_funcs[channel_num]) - 1:
                        # Last function, so do last function and then delete 
                        # layover data.
                        raw_processed_data = self.process_funcs[channel_num][
                                process_num](raw_processed_data)
                        raw_processed_data = raw_processed_data[
                                        self.layover_size:]
                        
                    elif process_num > 0:
                        # Middle function so no need to remove or add layover 
                        # data.
                        raw_processed_data = self.process_funcs[channel_num][
                                process_num](raw_processed_data)
                        
                    elif process_num == 0:    
                        # First function being applied, so concatenating data 
                        # with layover data.
                        raw_processed_data = np.concatenate((self.layover_data[
                                channel_num,:], raw_processed_data), axis=0)
                        # Processing.
                        raw_processed_data = self.process_funcs[channel_num][
                            process_num](raw_processed_data)
                        
                    
                    else:
                        print('Warning: \
                              Error applying process function e.g. filter')
                        
            self.processed_data[:,channel_num] = raw_processed_data
                
    
    def load_data(self,verbose=False):
        """
        Loads the raw files using the function defined in load_data_func.
        
        Loads the files into data and adds the specified amount of old data 
        into layover.
        """
        
        # Read data from next raw file
        if len(self.files_to_process) > 0:
            
            self.current_file = self.files_to_process[self.file_index]
            
            if verbose:
                print("Loading data from file #%d:\n" % self.file_index + 
                      "'%s'" % self.current_file)
            
        else:
            
            if verbose:
                print("(No data avaliable for pre-processing)")
            
            return False
        
        # Load data using load function
        (t,x) = self.load_data_func(self.current_file)
        self.timestamps = t
        self.data = x
        
        if self.first_run == True:
            # Can't add layover data as this is the first file
            pass
        
        else:
            # Update layover variable before loading new data
            self.layover = self.data[:,-self.layover_size:]
            
        # Clear previous processed data
        self.processed_data = np.empty((len(self.timestamps),
                                        self.max_channel_num))
        
        return True


    def save_data(self,
                  old_suffix = 'Completed.csv',
                  new_suffix = 'Processed.csv',
                  verbose=True):
        """
        Save the data to file and delete the original data.
        
        ***
        Optional:
        
        * `delete_raw`, _boolean_, if True raw data files will be deleted
          once they have been pre-processed
          
        * `old_suffix`, _string_, suffix for raw data files to be pre-processed
        
        * `new_suffix`, _string_, suffix for new data files following pre-processing
          
        """
                
        # Get file name of file being pre-processed
        raw_file = self.files_to_process[self.file_index]
        
        # Strip of folder name
        file_name = os.path.split(raw_file)[1]

        # Strip of old suffix
        file_name = file_name[:-len(old_suffix)]
        
        # Append output folder and new suffix
        file_name = self.output_folder + file_name
        file_name += new_suffix
        
        # Write datafile using defined write function
        self.save_data_func(file_name,
                            self.timestamps, 
                            self.processed_data, 
                            self.channel_names)
        
        if verbose:
            print("PRE:\tNew file created\n\t%s" % file_name)
        
        # Delete old file
        if self.delete_raw:
            os.remove(raw_file)
            self.file_index = 0  # process first file in list next time
            
            if verbose:
                print("PRE:\tRaw data file deleted\n\t%s" % raw_file)
            
        else:
            self.file_index += 1 # index of next file to be processed
    
    
#    def update_display(self):
#        """
#        Update the LiveFeed
#        
#        As this is only done every time the pre-processor loads a file this 
#        expected to be quite jumpy and there will be quite a lag.
#        """
#        
#        self.LiveFeed1.update_figures(self.timestamps,self.data,self.processed_data,self.first_run)  
#        self.first_run = False 

    
    def run(self, file_ready_obj, tick_timeout, timeout=120, verbose=True):
        """
        Main routine, defines the operation of the pre-processor.
        
        It runs until a tick_timeout object is set and looks for new files on a 
        file_ready_obj being set. Once a file is released for processing, it is: 
            loaded,
            processed,
            saved,
            liveFeed updated
        After a file is processed a check is made to see if any other files are 
        ready for processing (to deal with a backlog).
        A timeout has also been set in case of an error however it is possible for 
        the pre-processor thread to hang if the file_ready_object is not set to 
        release this thread.
        """
        
        start_time = time.time()  
        
        while not tick_timeout.isSet():
            
            current_t = time.time() - start_time
            
            file_ready_obj.wait()
            file_ready_obj.clear()
            
            while self.check_files():
            
                self.load_data()
                
                self.process_data()
                
                self.save_data(verbose=verbose)
                
                #PreProcessor1.update_display()
                
                if current_t > timeout:
                    
                    if verbose:
                        print('Warning: Pre-processor timed out')
                        
                    return
                
                current_t = time.time() - start_time
            
        if verbose:
            print('PRE:\tThread finished')
        
    
#%%    
    
if __name__ == "__main__":
        
    def addition_1(xx):
        yy = xx + 1
        return yy
    
    def subtract_1(xx):
        yy = xx - 1
        return yy
    
    process_funcs = [[addition_1, addition_1, addition_1],[subtract_1]]  
          
    PreProcessor1 = PreProcessor(process_funcs,delete_raw=True)
       
    PreProcessor1.check_files(verbose=True)
    
    data_loaded = PreProcessor1.load_data(verbose=True)
    #print(PreProcessor1.data)
    
    if data_loaded:
    
        PreProcessor1.process_data()
    #print(PreProcessor1.processed_data)
    
        PreProcessor1.save_data(verbose=True)