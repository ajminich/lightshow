#!/usr/bin/env python
"""
Performs all high-level GPIO control.

The color vectors would be easier to handle with numpy, but I'd rather steer
clear of that on a less-powerful piece of hardware like the Raspberry Pi.
"""

import argparse
from datetime import timedelta
import logging
import time

# Raspberry Pi imports
from RPi import GPIO

# GPIO Setup
BLUE_LED = 17
GREEN_LED = 4
RED_LED = 27

MIN_DUTY_CYCLE = 0
ONE_THIRD_DUTY_CYCLE = 33
HALF_DUTY_CYCLE = 50
TWO_THIRDS_DUTY_CYCLE = 66
MAX_DUTY_CYCLE = 100

# Color Vectors
OFF_VECTOR          = (MIN_DUTY_CYCLE, MIN_DUTY_CYCLE, MIN_DUTY_CYCLE)
BLUE_VECTOR         = (MIN_DUTY_CYCLE, MIN_DUTY_CYCLE, MAX_DUTY_CYCLE)
GREEN_BLUE_VECTOR   = (MIN_DUTY_CYCLE, HALF_DUTY_CYCLE, HALF_DUTY_CYCLE)
GREEN_VECTOR        = (MIN_DUTY_CYCLE, MAX_DUTY_CYCLE, MIN_DUTY_CYCLE)
RED_GREEN_VECTOR    = (HALF_DUTY_CYCLE, HALF_DUTY_CYCLE, MIN_DUTY_CYCLE)
RED_VECTOR          = (MAX_DUTY_CYCLE, MIN_DUTY_CYCLE, MIN_DUTY_CYCLE)
RED_BLUE_VECTOR     = (HALF_DUTY_CYCLE, MIN_DUTY_CYCLE, HALF_DUTY_CYCLE)
ON_VECTOR           = (ONE_THIRD_DUTY_CYCLE, ONE_THIRD_DUTY_CYCLE, ONE_THIRD_DUTY_CYCLE)

DEFAULT_PERIOD=timedelta(seconds=1)

class GPIOController(object):
    """
    A simple controller for GPIO operations.
    """

    def __init__(self):
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(RED_LED, GPIO.OUT)
        GPIO.setup(GREEN_LED, GPIO.OUT)
        GPIO.setup(BLUE_LED, GPIO.OUT)

        self.redPWM = GPIO.PWM(RED_LED, 60)
        self.greenPWM = GPIO.PWM(GREEN_LED, 60)
        self.bluePWM = GPIO.PWM(BLUE_LED, 60)

        # Start all PWMs at 0% duty cycle.
        self.redPWM.start(MIN_DUTY_CYCLE)
        self.greenPWM.start(MIN_DUTY_CYCLE)
        self.bluePWM.start(MIN_DUTY_CYCLE)

        self.colorVector = OFF_VECTOR

        # Use a resolution of 100 - this generally works well for periods of
        # 10 seconds or less.
        self.resolution = 1000

    def __del__(self):
        GPIO.cleanup(BLUE_LED)
        GPIO.cleanup(GREEN_LED)
        GPIO.cleanup(RED_LED)

    def setColorVector(self, colorVector):
        """
        Changes the duty cycles of the LED colors to attain the requested
        color vector.

        :type colorVector:
            tuple of duty cycles (R, G, B)
        """

        redVal = min(max(colorVector[0], MIN_DUTY_CYCLE), MAX_DUTY_CYCLE)
        greenVal = min(max(colorVector[1], MIN_DUTY_CYCLE), MAX_DUTY_CYCLE)
        blueVal = min(max(colorVector[2], MIN_DUTY_CYCLE), MAX_DUTY_CYCLE)

        self.redPWM.ChangeDutyCycle(redVal)
        self.greenPWM.ChangeDutyCycle(greenVal)
        self.bluePWM.ChangeDutyCycle(blueVal)

        # Update the internal color vector.
        self.colorVector = (redVal, greenVal, blueVal)

    def performCrossFade(self, period, targetVector):
        """
        Runs a single color crossfade.

        :type period:
            timedelta
        """

        startVector = self.colorVector

        redIncrement = float(targetVector[0] - startVector[0]) / self.resolution
        greenIncrement = float(targetVector[1] - startVector[1]) / self.resolution
        blueIncrement = float(targetVector[2] - startVector[2]) / self.resolution

        for index in xrange(self.resolution):
            newVector = (self.colorVector[0] + redIncrement,
                         self.colorVector[1] + greenIncrement,
                         self.colorVector[2] + blueIncrement)
            self.setColorVector(newVector)
            time.sleep(float(period.total_seconds()) / self.resolution)

    def runCrossFade(self, numIterations=1, period=DEFAULT_PERIOD):
        """
        Runs a set of crossfades.

        :type period:
            timedelta
        """

        effectivePeriod = period / 6

        for _ in xrange(numIterations):
            # Fade: blue -> blue-green -> green -> green-red -> red -> red-blue
            self.performCrossFade(period=effectivePeriod, targetVector=BLUE_VECTOR)
            self.performCrossFade(period=effectivePeriod, targetVector=GREEN_BLUE_VECTOR)
            self.performCrossFade(period=effectivePeriod, targetVector=GREEN_VECTOR)
            self.performCrossFade(period=effectivePeriod, targetVector=RED_GREEN_VECTOR)
            self.performCrossFade(period=effectivePeriod, targetVector=RED_VECTOR)
            self.performCrossFade(period=effectivePeriod, targetVector=RED_BLUE_VECTOR)

        self.performCrossFade(period-effectivePeriod, targetVector=OFF_VECTOR)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Runs LED crossfades.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-i', '--iters',
                        type=int,
                        default=1,
                        help='number of crossfade iterations')
    parser.add_argument('-p', '--period',
                        type=float,
                        default=2.0,
                        help='crossfade period in seconds')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        default=False,
                        help='enable verbose logging')

    args = parser.parse_args()

    # Set up logging
    FORMAT = "%(asctime)-15s %(filename)s:%(lineno)s [%(levelname)s] %(message)s"
    logLevel = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, level=logLevel)

    # Run GPIOs
    gpioController = GPIOController()
    gpioController.runCrossFade(numIterations=args.iters,
                                period=timedelta(seconds=args.period))