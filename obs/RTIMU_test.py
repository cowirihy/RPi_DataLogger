# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 11:38:16 2018

@author: ARIR
"""

import RTIMU
import time

timeout = 30
 
start_time = time.time()

s = RTIMU.Settings("RTIMU_settings")
imu = RTIMU.RTIMU(s)
print("IMU Name: " + imu.IMUName())

data = (0, 0, 0)

imu.IMUInit()

wait_s = imu.IMUGetPollInterval()/1000.0

print(wait_s)

current_time = time.time() - start_time

while current_time < timeout:
    if imu.IMURead():
        data = imu.getAccel()
        print(data)
    else:
        print('sampling too fast')
    time.sleep(wait_s)
    current_time = time.time() - start_time

print(data)

