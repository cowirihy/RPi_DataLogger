# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 12:35:40 2018

@author: rihy
"""

import threading
import time

start_time = time.time()
exec_times = []
    

def ticker(tick,T:float=1.0,timeout:float=10.0, tick_timeout = None):
    
    print("Ticker thread started")
    print("Time interval: %f" % T)
    print("Timeout: %f" % timeout)
    
    current_time = time.time() - start_time
    
    while current_time < timeout:
        
        current_time = time.time() - start_time
        exec_times.append(current_time)
        time.sleep(T)
        tick.set()
        
    print("Ticker thread timed-out")
    
    if tick_timeout is not None:
        tick_timeout.set()
    


def do_stuff(wait_time=0.1):
    
    print("\nDoing some time-consuming stuff...")
    print("wait_time =  %f" % wait_time)
    time.sleep(wait_time)
    print("Done at {0}".format(time.time()-start_time))


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
    ticker_thread = threading.Thread(name='ticker', 
                                     target=ticker,
                                     args=(e,),
                                     kwargs={'timeout':15.0,'T':0.5})
    ticker_thread.start()

    
    # Define a second processing thread
    proc_thread = threading.Thread(name='processing', 
                                   target=wait_for_event,
                                   args=(e,do_stuff,),
                                   kwargs={'wait_time':0.1})
    
    proc_thread.start()
    
   