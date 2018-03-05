
import time
import zmq

import sys
sys.path.insert(0, '../')

from uri_resolver import resolver

def createServer():

    #initalise server
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    #Listen for client requests
    while True:
        message = socket.recv()
        print("Received request: %s" % message)
        filepath = resolver.uri_to_filepath(message)
        socket.send(filepath)
