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
amber = (255, 128,   0)
black = (  0,   0,   0)

# Define shape of grid of pixels on SenseHat
n_pixel_rows = 8
n_pixel_cols = 8 

from matplotlib import cm


def pixel_bar(val:float,
              pixel_row:int,
              good_color=green,
              bad_color=amber,
              bad_flag:bool=False):
    """
    Displays row of pixels, length of which depends on
    values provided. Range of x expected [0,1]
    """
    
    val = int(n_pixel_cols * val) # convert to number of lights on pixel grid
        
    for i in range(n_pixel_cols):
        
        if i <= val:
            
            if bad_flag:
                c = bad_color
            else:
                c = good_color
                            
        else:
            c = black
            
        sense.set_pixel(i, pixel_row, c)



class Watchdog():
    
    def __init__(self,acq_obj,preproc_obj,ticker_obj,tick_timeout,refresh_dt=0.1):
        
        print("WTCH:\tWatchdog initialised")
        
        self.acq_obj = acq_obj
        self.preproc_obj = preproc_obj
        self.ticker_obj = ticker_obj
        
        self.tick_timeout = tick_timeout
        self.refresh_dt = refresh_dt
        
        # Get expected sampling period
        self.dt = ticker_obj.dt
        
        self.cmap = cm.jet  # colormap used for pixels
        
        
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
            self.check_raw_file_status()
            
            # Check acquisition speed
            #self.check_acq_speed()
            
            # Get for user inputs e.g. via joystick
            self.check_user_inputs()
                
            # Wait for preset time before running checks again
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
        
        
    def check_acq_speed(self,status_pixel=(0,1),verbose=False):
        """
        Monitors acquisition speed, checking ratio of time spent acquiring
        data to required sampling interval
        """
        
        # Calculate acquisiton speed as proportion of expected sampling interval
        max_time = self.acq_obj.max_acq_time
        rel_speed = max_time / self.dt
        
        if rel_speed > 1.0:
            print("WTCH:\tError: data acquisition loop too slow!\n"+
                  "\tMax acq time: %.4s (secs)" % max_time)
            c = red
        
        elif rel_speed > 0.8:
            c = amber
            
        else:
            c = green
        
        sense.set_pixel(*status_pixel, c)
        
        
    def check_raw_file_status(self,pixel_row=(n_pixel_rows-1)):
        
        p = self.acq_obj.get_proportion_complete()
        
        missing_data = self.acq_obj.has_missing_data()
        
        pixel_bar(p,pixel_row=pixel_row,bad_flag=missing_data)

            
            
    def check_user_inputs(self):
                
        for event in sense.stick.get_events():
            
            if event.direction == "middle" and event.action == "held":
            
                print("WTCH: Joystick pressed and held\n" +
                      "\tAcquisition will terminate " +
                      "once next file completed")
                self.tick_timeout.set()       # terminates acquisition
