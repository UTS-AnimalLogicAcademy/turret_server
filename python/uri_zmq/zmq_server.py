
import time
import zmq
from uri_resolver import resolver

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

while True:

    message = socket.recv()
    print("Received request: %s" % message)
    filepath = resolver.uri_to_filepath(message)

    socket.send(filepath)
