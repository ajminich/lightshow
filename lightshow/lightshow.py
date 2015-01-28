#!/usr/bin/env python

from flask import Flask, request
import logging

# Local imports
from gpio_controller import GPIOController

# Resource setup
FORMAT = "%(asctime)-15s %(filename)s:%(lineno)s [%(levelname)s] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

app = Flask("Lightshow")
gpioController = GPIOController()

# Routing

@app.route('/lightshow/<int:iterations>')
def lightshow(iterations):
    logging.info("received request to perform %d lightshow iterations", iterations)
    gpioController.runCrossFade(iterations)
    return "Watch the show!"

@app.route('/shutdown')
def shutdown():
    logging.info("received request to shut server down")
    shutdown_server()
    return 'Server shutting down...'

# Server operations

def start_server():
    app.debug = True
    app.run(host='0.0.0.0', port=80)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == "__main__":
    start_server()