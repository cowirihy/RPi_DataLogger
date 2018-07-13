# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 10:08:56 2018

@author: ARIR
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time

class LiveFeed():
    def __init__(self, chan_titles, 
                 fig_x_length, 
                 draw_function = {}, 
                 raw_data_channels = [], 
                 processed_data_channels = []):
        
        self.channels = chan_titles
        self.raw_channels = raw_data_channels
        self.processed_channels = processed_data_channels
        self.draw_func = draw_function
        self.fig_len = fig_x_length
       
        if not bool(draw_function):
        
            for channel in chan_titles:    
                self.draw_func[channel] = line_chart
    
    
    def update_figures(self, timestamps, 
                       new_raw_data = None, 
                       new_processed_data = None, 
                       first_run = False):
               
        if bool(self.raw_channels):
            new_raw_data = pd.DataFrame(data = new_raw_data,
                                        index=timestamps, 
                                        columns=self.channels)
            new_raw_data = new_raw_data[self.raw_channels]
                
            if first_run:
                self.raw_figs = GroupFigs(new_raw_data,
                                          self.fig_len, 
                                          self.raw_channels, 
                                          self.draw_func)    
            else:
                self.raw_figs.update_group(new_raw_data)
                    
            
        if bool(self.processed_channels):
            new_processed_data = pd.DataFrame(data = new_processed_data, 
                                          index = timestamps,
                                          columns = self.channels)
            new_processed_data = new_processed_data[self.processed_channels]
            if first_run:
                self.processed_figs = GroupFigs(new_processed_data, 
                                                self.fig_len, 
                                                self.processed_channels, 
                                                self.draw_func)
                self.processed_figs.update_group(new_processed_data)


class GroupFigs():
    def __init__(self, new_data, fig_len, selected_channels, draw_func):
        self.held_data = RingBuffer(new_data, fig_len)
        print(new_data)
        self.group_figures = {None:None}
        self.selected_channels = selected_channels
        for channel in selected_channels:
                subplot_args = [111]
                fig_kwargs={'num': channel + ': raw'}
                current_fig = LiveFig(draw_func[channel],
                                  args_subplot = subplot_args,
                                  kwargs_fig = fig_kwargs)
                data = self.held_data.current_buffer()[channel]
                data = [list(data.index),data.tolist()]
                current_fig.update_fig(data)
                self.group_figures[channel] = current_fig
    
    def update_group(self, new_data):
        self.held_data.add_data(new_data)
        
        for channel in self.selected_channels:
                current_fig = self.group_figures[channel]
                data = self.held_data.current_buffer()[channel]
                data = [list(data.index),data.tolist()]
                current_fig.update_fig(data)


class RingBuffer():
    def __init__(self, data, max_length):
        self.max_rows = max_length
        
        if isinstance(data, pd.DataFrame):
            self.buffer = data
            if data.shape[0] > max_length:
                print('Warning: Initial data too large, some data disgarded')
                self.buffer = self.buffer.iloc[:,-max_length:]
        else:
            print('Warning: Setup failed as initial data not Pandas DataFrame')
    
    
    
    def add_data(self, data):
        if isinstance(data,pd.DataFrame):
            self.buffer = self.buffer.append(data)
            if self.buffer.shape[0]>self.max_rows:
                self.buffer = self.buffer[-self.max_rows:]
                
        else:
            print('Warning: Attempted to add unsupported data type to ring_buffer')
    
    def current_buffer(self):
        return self.buffer
    
    def index(self):
        return list(self.buffer.index)
    
class LiveFig():
    
    def __init__(self, draw_function,
                 args_subplot = None,
                 kwargs_subplot = {None:None},
                 kwargs_fig = {None:None}):
        
        self.fig = plt.figure(**kwargs_fig)
        self.ax = self.fig.add_subplot(*args_subplot)
        self.ax.grid()
        self.draw_func = draw_function
        
    def update_fig(self,data):
        self.draw_func(data, self.fig, self.ax)
        
    def destroy_fig(self):
        plt.clear(self.fig)

import datetime

def line_chart(data, fig, ax):
    
    ax.cla()
    x = data[0][:]
    y = data[1][:]
    
    x = np.linspace(0,100,len(x))
    
    ax.plot(x, y, 'k')
    fig.canvas.draw()
    fig.canvas.flush_events()
    
        
if __name__ == '__main__':
    
    timestamp = ['1','2','3']
    timestamp2 = ['5','6','7','8']
    timestamp3 = ['9','10','11','12']    
    data1 = np.array([[100,600],[200,700],[300,200]])
    data2 = data1 + 23
    
    fig_x_len = 5
    draw_function={'Ch1':line_chart,'Ch2':line_chart}
    
    LiveFeed1 = LiveFeed(['Ch1','Ch2'], 
                         fig_x_len,
                         raw_data_channels = ['Ch1','Ch2'])
    time.sleep(3)    
    LiveFeed1.update_figures(timestamp, data1, data2, True)
    time.sleep(1)
    print(LiveFeed1.raw_figs.held_data.current_buffer())
#    print(LiveFeed1.processed_figs.held_data.current_buffer())
    data1 = np.array([[1,6],[2,0],[3,0],[0,5]])
    data2 = data1 + 23
    
    LiveFeed1.update_figures(timestamp2, data1, data2, False)
    print(LiveFeed1.raw_figs.held_data.current_buffer())
 #   print(LiveFeed1.processed_figs.held_data.current_buffer())
    time.sleep(1)
    LiveFeed1.update_figures(timestamp3, data1, data2, False)
    print(LiveFeed1.raw_figs.held_data.current_buffer())
#    print(LiveFeed1.processed_figs.held_data.current_buffer())
    

