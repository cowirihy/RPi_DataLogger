# -*- coding: utf-8 -*-
"""
Created on Mon Jun 25 10:15:21 2018

@author: ARIR
"""

import os
import numpy as np
import pandas as pd
import time
import liveFeed
#%%

def default_load(file_name):
    """
    The default loading method: Assumes 1 line of header with the first column taken as the index.
    It takes None strings as a numppy nan object - important for the rest of the code to run robustly.
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
                 draw_function,   
                 dsp_raw_channels,   
                 dsp_processed_channels,  
                 load_data_func=default_load,   
                 save_data_func=default_save,   
                 fig_x_len = 1000,   
                 layover_size = 20,    
                 acquisition_folder = 'data_raw/',
                 output_folder = 'data_preprocessed/',   
                 keyword = "Completed"): 

        
        self.data = np.array(None)
        self.process_funcs = process_funcs
        self.layover_size = layover_size
        self.acquisition_folder = acquisition_folder
        self.output_folder = output_folder
        self.keyword = keyword        
        self.first_run = True
        self.load_data_func = load_data_func 
        self.save_data_func = save_data_func
        self.layover_data = np.empty((len(self.process_funcs), layover_size))
        self.max_channel_num = len(self.process_funcs)
        self.channel_strs = [None]*self.max_channel_num
        
        for channel_num in range(0,len(self.process_funcs)):
            self.channel_strs[channel_num] = 'Ch' + str(channel_num)
            
        self.LiveFeed1 = liveFeed.LiveFeed(self.channel_strs,   
                                           fig_x_len,  
                                           raw_data_channels = dsp_raw_channels,   
                                           processed_data_channels = dsp_processed_channels) 

    
    def check_files(self):
            
        fldr = self.acquisition_folder
        file_names = os.listdir(fldr)
        self.completed_files = [fldr + s for s in file_names if self.keyword in s]
        
        
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
            
    
    def load_files(self):
        """
        Loads the raw files using the function defined in load_data_func.
        
        Loads the files into data and adds the specified amount of old data 
        into layover.
        """
        
        (self.timestamps, self.data) = self.load_data_func(self.completed_files[0])
        
        if self.first_run == True:
            # Can't add layover data as this is the first file
            pass
        
        else:
            # Update layover variable before loading new data
            self.layover = self.data[:,-self.layover_size:]
            
        self.processed_data = np.empty((len(self.timestamps),self.max_channel_num))


    def save_files(self,
                   delete_raw=False,
                   old_suffix = 'Completed.csv',
                   new_suffix = 'Processed.csv'):
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
        raw_file = self.completed_files[0]
        
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
                            self.channel_strs)
        
        # Delete old file
        if delete_raw:
            os.remove(raw_file)
    
    
    def update_display(self):
        """
        Update the LiveFeed
        
        As this is only done every time the pre-processor loads a file this 
        expected to be quite jumpy and there will be quite a lag.
        """
        
        self.LiveFeed1.update_figures(self.timestamps,self.data,self.processed_data,self.first_run)  
        self.first_run = False 

    
#%%    

def run_pre_processor(PreProcessor1, file_ready_obj, tick_timeout, timeout=120):
    """
    The general loop that defines the operation of the pre-processor.
    
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
        PreProcessor1.check_files()
        if current_t > timeout:
            print('Warning: Processor timed out')
            return
        while PreProcessor1.completed_files:
            PreProcessor1.load_files()
            PreProcessor1.process_data()
            PreProcessor1.save_files()
            PreProcessor1.update_display()
            print('Processor: file processed and saved')
            PreProcessor1.check_files()
            if current_t > timeout:
                print('Warning: Processor timed out')
                return
            current_t = time.time() - start_time
        
    
    print('PreProcessor: Finished and shut down')
    
    
#%%    
    
if __name__ == "__main__":
        
    def addition_1(xx):
        yy = xx + 1
        return yy
    
    def subtract_1(xx):
        yy = xx - 1
        return yy
    
    process_funcs = [[addition_1, addition_1, addition_1],[subtract_1]]  
    draw_function={'Ch1':liveFeed.line_chart,'Ch2':liveFeed.line_chart}  
    dsp_raw_channels = list(draw_function.keys())  
    dsp_processed_channels = list(draw_function.keys())  
      
    PreProcessor1 = PreProcessor(process_funcs,  
                                draw_function,  
                                dsp_raw_channels,  
                                dsp_processed_channels, 
                                layover_size = 3)
    
   
    for ii in range(0,1):
        PreProcessor1.check_files()
        PreProcessor1.load_files()
        print(PreProcessor1.data)
        PreProcessor1.process_data()
        print(PreProcessor1.processed_data)
        PreProcessor1.save_files()
        PreProcessor1.update_display()