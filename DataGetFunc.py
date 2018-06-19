# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:14:50 2018

@author: arir
"""
from sense_hat import SenseHat
from random import uniform

def PressureTake():

    
    sense = SenseHat()
    sense.clear
    
    return sense.get_pressure()


def TempFromHumidityTake():
    sense = SenseHat()
    sense.clear
    
    return sense.get_temperature()

def TempFromPressureTake():
    sense = SenseHat()
    sense.clear
    
    return sense.get_temperature_from_pressure()

def HumidityTake():
    
    sense = SenseHat()
    sense.clear()
    
    return sense.get_humidity()

def OrientationTake():
    sense = SenseHat()
    sense.clear()
    
    orient = sense.get_orientation()
    pitch = orient["pitch"]
    roll = orient["roll"]
    yaw = orient["yaw"]
    
    return pitch, roll, yaw

def AccelTake():
    sense = SenseHat()
    sense.clear
    
    acceleration = sense.get_accelerometer_raw()
    x = acceleration['x']
    y = acceleration['y']
    z = acceleration['z']
    
    return x, y, z

def randomNum():
    return uniform(-10,40)
