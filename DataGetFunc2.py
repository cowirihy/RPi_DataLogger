# -*- coding: utf-8 -*-
"""
Created on Thu Jun 14 09:14:50 2018

@author: arir
"""
try:
    import RTIMU
except:
    class placeHolderIMU():
        def __init__(self):
            return
        
        def IMUName(self):
            return 'FAKE'
        def IMUInit(self):
            return False
    
    class RTIMU():
        def __init__(self):
            return
        def Settings(s):
            return s
        def RTIMU(s):
            return placeHolderIMU()
    
from random import uniform
import time


def randomNum():
    return uniform(-10,40)


class AccelReader():
    def __init__(self, imu, fake_IMU=False):
        
        if not fake_IMU:
            self.imu = imu
            print(imu.IMUGetPollInterval()/1000.0)
        
        self.data = (0, 0, 0)
        self.fake_IMU = fake_IMU

    def all_accel_take(self):       
        
        if not self.fake_IMU:
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
            print(reader.x_accel_take(fetch_new_data = True))
            time.sleep(0.1)

    some_program(lambda: reader.all_accel_take())