# -*- coding: utf-8 -*-
"""
Created on Wed Jun 20 15:48:07 2018

@author: ARIR
"""
import pandas as pd
import numpy as np

class RingBuffer():
    """
    Holds a list of a certain size only
    """
    
    def __init__(self, load_data_func, buffer_size=10):
        self.load_data_func = load_data_func
        self.__num_in_list = 0
        self.buffer_size = buffer_size
        
    def append_data(self,file_name):
        """ 
            Gets and appends data to the buffer. 
            If buffer is full delets first element.
        """
        if self.__num_in_list == 0:
            self.buffer = np.array(self.load_data_func(file_name))
            self.__num_in_list += 1
            
        elif self.__num_in_list < self.buffer_size:
            self.buffer = np.append(self.buffer,self.load_data_func(file_name), axis = 0)
            self.__num_in_list += 1
        elif self.__num_in_list >= self.buffer_size:
            np.delete(self.buffer,0,0)
            self.buffer = np.append(self.buffer,self.load_data_func(file_name), axis = 0)
        
def get_file_data(fileName = "2018_06_21_10_02_34.csv"):
    loaded_file = pd.read_csv(fileName, skiprows = 1)
    return loaded_file


if  __name__ ==  "__main__":
    
    import random
    def load_data():
        some_data = ["A string", random.uniform(0,100), random.uniform(0,100)]
        return some_data
    
    buffer1 = RingBuffer(load_data, 5)
    
    for ii in range(0,4):
        buffer1.append_data()
    print(buffer1.buffer)
    
    for jj in range(0,3):
        buffer1.append_data()
    print(buffer1.buffer)


