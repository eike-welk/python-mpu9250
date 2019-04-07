# A calibation library for the various sensors of a IMU.

import time
from math import pi
from collections import namedtuple
from enum import Enum
from multiprocessing.dummy import Pool

import numpy as np

import ak8963
import mpu6500

MsgCalib = namedtuple('msgCalib', ['text', 'sound'])
MsgUser = namedtuple('msgUser', ['text', 'command'])

class Sound(Enum):
    quiet = 0
    continue_sound = 1
    error = 11
    measurement = 12
    question = 13

class UserCommand(Enum):
    quit = 11


# class DataReader:
#     """
#     Read measuremnt data from the sensors.
#     Pass the data to the calibration function in chunks.
#     """
#     def __init__(self):
#         self.running = False

#     def run(self):
#         while self.running:
#             # Read the sensors
#             # Put data into temporary buffer
#             # If enough data is collected, pass it to the cllibration thread.
#             pass

class Calibrator:
    """
    Perform the calibration of IMU sensors.

    This class needs a frontend that communicates with the user.
    """
    def __init__(self):
        self.imu = mpu6500.MPU6500()
        self.mag = ak8963.AK8963()

        self.read_n_samples = 20
        self.read_interval = 1.0 / 20      # 1 / 20 Hz
        self.calib_rot_max = pi / 180 / 10 # 0.1 deg / s
        self.calib_acc_max = 0.01          # 1 cm / s / s

    def readSensorData(self):
        n = self.read_n_samples
        tim = np.zeros(n, int)
        acc = np.zeros((n, 3), int)
        rot = np.zeros((n, 3), int)
        mag = np.zeros((n, 3), int)
        for i in range(n):
            tim[i] = time.time()
            acc[i, ...] = self.imu.read_acceleration_raw()
            rot[i, ...] = self.imu.read_gyro_raw()
            mag[i, ...] = self.mag.read_magnetic_raw()
            time.sleep(self.read_interval)
        return tim, acc, rot, mag

    def run(self):
        # Concepts for data aquisition and evaluation

        # Storage for the accumulated sensor values.
        # Initialized to lenght 0 along the measurement axis.
        tim_all = np.zeros((0, 1))
        acc_raw_all = np.zeros((0, 3))  
        rot_raw_all = np.zeros((0, 3))
        mag_raw_all = np.zeros((0, 3))

        # Read the sensor values in a separate thread.
        thread_pool = Pool()

        res = thread_pool.apply_async(self.readSensorData)
        if self.user_want_quit():
            return

        tim, acc_raw, rot_raw, mag_raw = res.get()

        # Scale acceleration and rotation for analysis.
        acc = np.zeros_like(acc_raw)
        rot = np.zeros_like(rot_raw)
        for i in range(acc.shape[0]):
            acc[i] = self.imu.compute_acceleration(acc_raw[i])
            rot[i] = self.imu.compute_gyro(rot_raw[i])

        # Statistical analysis of rotation and acceleration
        acc_mean = acc.mean(axis=0)
        rot_mean = rot.mean(axis=0)
        acc_std = acc.std(axis=0)
        rot_std = rot.std(axis=0)

        # If the device was held still enough, store the new sensor values.
        tim_all = np.concatenate((tim_all, tim), axis=0)
        acc_raw_all = np.concatenate((acc_raw_all, acc_raw), axis=0)
        rot_raw_all = np.concatenate((rot_raw_all, rot_raw), axis=0)
        mag_raw_all = np.concatenate((mag_raw_all, mag_raw), axis=0)

        # Take some measurements to estimate the noise
        # and to calibrate the gyroscope

        # Estimate if one of the senors is too noisy.
        # Display the noise of each sensor

        # Repeat
        # Take measurements from different orientations of the device
        # Every time the system does not move for 1 second start a measurement.
        # A measurement takes 5 seconds.
        # The device must not move at all, to calibrate the accelerometer.

        # The magnetometer values are recorded too.

        # When there are enough measurements from different directions, the 
        # calibration parameters can be computed.

        # multiprocessing.pool.Pool

        pass

    def communicate(self, msg:MsgCalib):
        """Send a message to the front end."""
        print(msg.text)

    def user_want_quit(self):
        """Test if the user wants to end the calibration process."""
        return False


class CalibFrontText:
    """
    Communicate with the user during the calibration process of an IMU.

    Uses text that appears in a terminal.
    """
    pass
