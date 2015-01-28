#!/usr/bin/env python

import argparse
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

def start_server(host, port):
    app.debug = True
    app.run(host=host, port=port)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

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
