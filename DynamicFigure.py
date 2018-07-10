# -*- coding: utf-8 -*-
"""
Created on Tue Jun 19 16:42:23 2018

@author: ARIR
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

#def init():
#    line.set_data([], [])
#    time_text.set_text('')
#    return line, time_text
#
#def animate(i):
#    thisx = [0, x1[i], x2[i]]
#    thisy = [0, y1[i], y2[i]]
#
#    line.set_data(thisx, thisy)
#    time_text.set_text(time_template % (i*dt))
#    return line, time_text

def line_chart(x, y):
    fig = plt.figure()
    ax = fig.add_subplot(111, autoscale_on=False, xlim=(-2, 2), ylim=(-2, 2))
    ax.grid()
    line = ax.plot([],[], 'o-', lw=2)
    line.set_data([],[])
    line.set_data(x, y)
    

line_chart([1,2,3,4],[9,8,7,6])

#timeout = 10
#
#start_time = time.time()
#
#fig = plt.figure()
#ax = fig.add_subplot(111, autoscale_on=False, xlim=(-2, 2), ylim=(-2, 2))
#ax.grid()
#
#while current_time < timeout:
#    
#    
#    
#    
#
#line, = ax.plot([], [], 'o-', lw=2)
#time_template = 'time = %.1fs'
#time_text = ax.text(0.05, 0.9, '', transform=ax.transAxes)
#
#
#
#ani = animation.FuncAnimation(fig, animate, np.arange(1, len(y)),
#                              interval=25, blit=True, init_func=init)
#plt.show()