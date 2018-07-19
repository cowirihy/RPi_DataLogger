# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:14:50 2018

@author: arir
"""
#from sense_hat import SenseHat
from random import uniform
#import RTIMU
import time

class RTIMU:
    
    def __init__(self):
        return
    def Settings():
        return
    def RTIMU(self, something):
        return self
    def IMUInit():
        return False
    def IMUName():
        return 'fakeIMU'
    def IMUGetPollInterval():
        return 0.000001
    
def randomNum():
    return uniform(-10,40)


class AccelReader():
    def __init__(self, imu, fake_IMU=False):
        
        self.imu = imu
        self.data = (0, 0, 0) 
        print(imu.IMUGetPollInterval()/1000.0)

    def all_accel_take(self):        
        
        if not fake_IMU: 
            if self.imu.IMURead(): 
                self.data = self.imu.getAccel()
            else:
                print('Warning: failed to get data')
                self.data = (None, None, None)
        else:
            self.data = (uniform(-10,40),uniform(-10,40),uniform(-10,40))
            
    def x_accel_take(self, fetch_new_data = False):
        if fetch_new_data:
            self.all_accel_take()
        xx = self.data[0]
        return xx 
        
    def y_accel_take(self, fetch_new_data = False):
        if fetch_new_data:
            self.all_accel_take()
        yy = self.data[1]
        return yy     
        
    def z_accel_take(self, fetch_new_data = False):
        if fetch_new_data:
            self.all_accel_take()
        zz = self.data[2]
        return zz
 
                  
if __name__ == '__main__':
    
    s = RTIMU.Settings('RTIMU_settings')
    imu = RTIMU.RTIMU(s) 
    print("IMU Name: " + imu.IMUName()) 
    fake_IMU = False

    if (not imu.IMUInit()): 
        print("IMU Init Failed!!!!")
        print("Starting fake IMU")
        fake_IMU = True
    else: 
        print("IMU Init Succeeded");
    
    reader = AccelReader(imu,fake_IMU)
    
    def some_program(get_data):
        
        for t in range(0,10):
            get_data()
            time.sleep(0.1)

    some_program(lambda : reader.all_accel_take(imu))