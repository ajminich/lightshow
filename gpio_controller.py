"""
Performs all high-level GPIO control.
"""

from datetime import timedelta
import logging
import time

# Raspberry Pi imports
from RPi import GPIO

# GPIO Setup
BLUE_LED = 17
GREEN_LED = 4
RED_LED = 27


class GPIOController(object):
    """
    A simple controller for GPIO operations.
    """

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(BLUE_LED, GPIO.OUT)
        GPIO.setup(GREEN_LED, GPIO.OUT)
        GPIO.setup(RED_LED, GPIO.OUT)

        self.bluePWM = GPIO.PWM(BLUE_LED, 60)
        self.greenPWM = GPIO.PWM(GREEN_LED, 60)
        self.redPWM = GPIO.PWM(RED_LED, 60)

    def __del__(self):
        GPIO.cleanup()

    def runSingleCrossFade(self, period, resolution):
        """
        Runs a single color crossfade.

        :type period:
            timedelta
        """
        for index in xrange(resolution):
            self.bluePWM.ChangeDutyCycle(100.0 * (resolution - index) / resolution)
            self.greenPWM.ChangeDutyCycle(100.0 * index / resolution)
            self.redPWM.ChangeDutyCycle(100.0 * index / resolution)
            time.sleep(float(period.total_seconds()) / resolution)

    def runCrossFade(self,
                     numIterations=1,
                     period=timedelta(seconds=2),
                     resolution=100):
        """
        Runs a set of crossfades.

        :type period:
            timedelta
        """

        self.bluePWM.start(100.0)
        self.greenPWM.start(0.0)
        self.redPWM.start(0.0)

        for _ in xrange(numIterations):
            self.runSingleCrossFade(period=period, resolution=resolution)
