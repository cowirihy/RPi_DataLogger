# -*- coding: utf-8 -*-
"""
Functions to acquire data, either using RPi RTIMU interface or using 
RTIMU emulator

@author: arir
"""

# Attempt to load RTIMU module
# (Will not work generally when not executing from RPi)
try:
    import RTIMU
    
except:
    
    class IMU_mimic():
        
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
            return IMU_mimic()
        
    
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
                acc_xyz = self.imu.getAccel()
                
            else:
                #print('Warning: failed to get data')
                acc_xyz = (None, None, None)
                
        else:
            acc_xyz = (uniform(-10,40),uniform(-10,40),uniform(-10,40))
        
        self.data = acc_xyz
        
        return acc_xyz
    
            
    def x_accel_take(self, fetch_new_data = False):
    
        if fetch_new_data:
            self.all_accel_take()
            
        acc_x = self.data[0]
        
        return acc_x
        
    
    def y_accel_take(self, fetch_new_data = False):
    
        if fetch_new_data:
            self.all_accel_take()
            
        acc_y = self.data[1]
        
        return acc_y    
    
        
    def z_accel_take(self, fetch_new_data = False):
    
        if fetch_new_data:
            self.all_accel_take()
            
        acc_z = self.data[2]
        
        return acc_z
 
                  
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
    
    
    def test_routine(get_data_func,**kwargs):
        
        for t in range(0,10):
            print(get_data_func(**kwargs))
            time.sleep(0.2)

    test_routine(reader.all_accel_take)