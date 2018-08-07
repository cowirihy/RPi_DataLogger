# -*- coding: utf-8 -*-
"""
Classes and functions used to implement Watchdog functionality
(i.e. monitor key processes)

@author: rihy
"""

try:
    from sense_hat import SenseHat

except:

    # Dummy class in case of not using RPi
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

red = (255, 0, 0)
green = (0, 255, 0)


class Watchdog():
    
    def __init__(self,acq_obj,preproc_obj,tick_timeout):
        
        print("WTCH:\tWatchdog initialised")
        
        self.acq_obj = acq_obj
        self.preproc_obj = preproc_obj
        self.tick_timeout = tick_timeout
        
        
    def run(self,verbose=True):
        
        if verbose: 
            print("WTCH:\tThread started")
        self.running = True
        
        while not self.tick_timeout.isSet():
            
            # Check status of acquisition system
            if not self.acq_obj.running:
                
                if verbose:
                    print("WTCH:\tAcqusition thread not running!")
                
                sense.set_pixel(0, 0, red)
                
            else:
                sense.set_pixel(0, 0, green)
                
            # Check status of pre-processor
            if not self.preproc_obj.running:
                
                if verbose:
                    print("WTCH:\tPreprocessor thread not running!")
                    
                sense.set_pixel(1, 0, red)
                
            else:
                sense.set_pixel(1, 0, green)
            
        if verbose:
            print('WTCH:\tThread finished')
            
        self.running = False
        sense.clear()