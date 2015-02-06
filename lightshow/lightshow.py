#!/usr/bin/env python

import argparse
from datetime import timedelta
from flask import Flask, request, render_template
import logging

# Local imports
import gpio_controller

# Resource setup
FORMAT = "%(asctime)-15s %(filename)s:%(lineno)s [%(levelname)s] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

app = Flask("Lightshow")

gpioController = gpio_controller.GPIOController()

# Form

from wtforms import Form, IntegerField, FloatField, validators

class LightshowForm(Form):
    iterations = IntegerField('Iterations', [validators.Required()], default=1)
    period = FloatField('Period (seconds)', [validators.Required()], default=5.0)

# Routing

@app.route('/', methods=['GET', 'POST'])
def lightshow():
    form = LightshowForm(request.form)

    if request.method == 'POST' and form.validate():
        # Determine which button was pressed
        if "Crossfade" in request.form:
            gpioController.runCrossFade(numIterations=form.iterations.data,
                                        period=timedelta(seconds=form.period.data))
        elif "Turn White" in request.form:
            gpioController.performCrossFade(gpio_controller.DEFAULT_PERIOD, gpio_controller.ON_VECTOR)
        elif "Turn Blue" in request.form:
            gpioController.performCrossFade(gpio_controller.DEFAULT_PERIOD, gpio_controller.BLUE_VECTOR)
        elif "Turn Green" in request.form:
            gpioController.performCrossFade(gpio_controller.DEFAULT_PERIOD, gpio_controller.GREEN_VECTOR)
        elif "Turn Red" in request.form:
            gpioController.performCrossFade(gpio_controller.DEFAULT_PERIOD, gpio_controller.RED_VECTOR)
        elif "Turn Off" in request.form:
            gpioController.performCrossFade(gpio_controller.DEFAULT_PERIOD, gpio_controller.OFF_VECTOR)

    return render_template('lightshow.html', form=form)

# Server operations

def start_server(host, port):
    app.debug = True
    app.run(host=host, port=port)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Runs a server to perform light shows.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host',
                        type=str,
                        default='0.0.0.0',
                        help='host IP address')
    parser.add_argument('-p', '--port',
                        type=int,
                        default=80,
                        help='host port')

    args = parser.parse_args()
    start_server(host=args.host, port=args.port)
