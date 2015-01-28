#!/usr/bin/env python
"""
Performs all high-level GPIO control.
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
        self.redPWM.start(0.0)
        self.greenPWM.start(0.0)
        self.bluePWM.start(0.0)

        self.colorVector = (0.0, 0.0, 0.0)

        # Use a resolution of 100 - this generally works well for periods of
        # 10 seconds or less.
        self.resolution = 100

    def setColorVector(self, colorVector):
        """
        Changes the duty cycles of the LED colors to attain the requested
        color vector.

        :type colorVector:
            tuple of duty cycles (R, G, B)
        """

        logging.debug("Moving to color vector (%f, %f, %f)", colorVector[0], colorVector[1], colorVector[2])

        self.redPWM.ChangeDutyCycle(colorVector[0])
        self.greenPWM.ChangeDutyCycle(colorVector[1])
        self.bluePWM.ChangeDutyCycle(colorVector[2])

        # Update the internal color vector.
        self.colorVector = colorVector

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

    def runCrossFade(self,
                     numIterations=1,
                     period=timedelta(seconds=2)):
        """
        Runs a set of crossfades.

        :type period:
            timedelta
        """

        for _ in xrange(numIterations):
            self.performCrossFade(period=period / 2, targetVector=(0, 0, 100))
            self.performCrossFade(period=period / 2, targetVector=(100, 100, 0))

        self.performCrossFade(period-period / 2, targetVector=(0, 0, 0))

        GPIO.cleanup(BLUE_LED)
        GPIO.cleanup(GREEN_LED)
        GPIO.cleanup(RED_LED)


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