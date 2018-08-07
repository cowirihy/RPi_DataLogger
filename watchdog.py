# -*- coding: utf-8 -*-
"""
Classes and functions used to implement Watchdog functionality
(i.e. monitor key processes)

@author: rihy
"""

import time

try:
    from sense_hat import SenseHat

except:

    # Dummy class (used when testing code by not running from RPi)
    class SenseHat():
        
        def __init__(self):
            print("WTCH:\t(Cannot use pixel display as no SenseHat)")
            pass
        
        def clear(self):
            pass
        
        def set_pixel(self,x,y,color):
            pass
    
    
sense = SenseHat()
sense.clear()

red   = (255,   0,   0)
green = (  0, 255,   0)
amber = (244, 182,  66)
black = (  0,   0,   0)

# Define shape of grid of pixels on SenseHat
n_pixel_rows = 8
n_pixel_cols = 8 


class Watchdog():
    
    def __init__(self,acq_obj,preproc_obj,tick_timeout,refresh_dt=0.1):
        
        print("WTCH:\tWatchdog initialised")
        
        self.acq_obj = acq_obj
        self.preproc_obj = preproc_obj
        self.tick_timeout = tick_timeout
        self.refresh_dt = refresh_dt
        
        
    def run(self,verbose=True):
        
        if verbose: 
            print("WTCH:\tThread started")
        self.running = True
        
        while not self.tick_timeout.isSet():
            
            # Check status of acquisition system
            self.check_acq_status(verbose=verbose)
                
            # Check status of pre-processor
            self.check_preproc_status(verbose=verbose)
                
            # Get % complete for raw file currently being written
            
                
            # Wait for preset time before checking statuses again
            time.sleep(self.refresh_dt)
            
        if verbose:
            print('WTCH:\tThread finished')
            
        self.running = False
        sense.clear()
        
    
    def check_acq_status(self,status_pixel=(0,0),verbose=True):
        
        if not self.acq_obj.running:
            
            if verbose:
                print("WTCH:\tAcqusition thread not running!")
            
            c = red
            
        else:
            c = green
        
        sense.set_pixel(*status_pixel, c)
        
    
    def check_preproc_status(self,status_pixel=(1,0),verbose=True):
        
        if not self.preproc_obj.running:
                
            if verbose:
                print("WTCH:\tPreprocessor thread not running!")
                
            c = red
            
        else:
            c = green
        
        sense.set_pixel(*status_pixel, c)
        
        
    def check_raw_file_status(self,pixel_row=(n_pixel_rows-1)):
        
        p = self.acq_obj.get_proportion_complete()
        nx = int(n_pixel_cols * p) # convert to number of lights on pixel grid
        
        missing_data = self.acq_obj.missing_data
        
        for x in range(n_pixel_cols):
            
            if x <= nx:
                
                if not missing_data:
                    c = green
                else:
                    c = amber
                                
            else:
                c = black
                
            sense.set_pixel(x, pixel_row, c)
        