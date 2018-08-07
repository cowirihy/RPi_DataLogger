# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 12:35:40 2018

@author: rihy
"""

import threading
import time


exec_times = []
    

class Ticker():
    
    def __init__(self,
                 tick_event,
                 dt:float=1.0,
                 timeout:float=10.0,
                 tick_timeout_event = None):
        
        self.dt = dt
        self.fs = 1/dt
        self.timeout = timeout
        
        self.tick_event = tick_event
        self.tick_timeout_event = tick_timeout_event
        
        print("TICK:\tTicker initialised\n" + 
              "\tSampling freq:\t%.2f\tHz\n" % self.fs +
              "\tTime interval:\t%.4f\tsecs\n" % self.dt +
              "\tTimeout:\t%.2f\tsecs" % self.timeout)
        
        
    def run(self):
        
        print("TICK:\tThread started")
        self.running = True
    
        start_time = time.time()
    
        current_time = time.time() - start_time
        
        while current_time < self.timeout:
            
            current_time = time.time() - start_time
            exec_times.append(current_time)
            time.sleep(self.dt)
            self.tick_event.set()
            
        print("TICK:\tThread timed-out")
        
        if self.tick_timeout_event is not None:
            self.tick_timeout_event.set()
    


def do_stuff(wait_time=0.1):
    
    print("\nDoing some time-consuming stuff...")
    print("wait_time =  %f" % wait_time)
    time.sleep(wait_time)
    print("Done at {0}".format(time.time()))


def wait_for_event(tick_obj,func,*fargs,**fkwargs):
        
    while not tick_obj.isSet():
    
        # Wait for next tick
        tick_obj.wait()
        tick_obj.clear() # resets tick flag
    
        # Do some stuff, as given by func
        func(*fargs,**fkwargs)
    

if __name__ == '__main__':
    
    # Define event to use in ticker thread
    e = threading.Event()
    
    # Define and start ticker thread
    
    ticker_obj = Ticker(tick_event=e,dt=0.5,timeout=15.0)
    
    ticker_thread = threading.Thread(name='ticker', 
                                     target=ticker_obj.run)
    ticker_thread.start()

    
    # Define a second processing thread
    proc_thread = threading.Thread(name='processing', 
                                   target=wait_for_event,
                                   args=(e,do_stuff,),
                                   kwargs={'wait_time':0.1})
    
    proc_thread.start()
    
   