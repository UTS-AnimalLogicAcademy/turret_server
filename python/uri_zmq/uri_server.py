
import time
import zmq

import sys
import threading

import sys
sys.path.insert(0, '../')

from uri_resolver import resolver

ZMQ_PORT = 5555
SERVER_RUNNING = False

def createServer():

    # Initalize server
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:%s" % ZMQ_PORT)

    global SERVER_RUNNING
    SERVER_RUNNING = True

    # Listen for client requests
    while SERVER_RUNNING:
        message = socket.recv()
        filepath = resolver.uri_to_filepath(message)

        print("Handled request %s -> %s" % (message, filepath))
        socket.send(filepath)

    # Clsoe server 
    socket.close()

def closeServer():
    global SERVER_RUNNING
    SERVER_RUNNING = False
    server.join()

class ServerTask(threading.Thread):
    """ServerTask"""
    def __init__(self):
        threading.Thread.__init__ (self)

    def run(self):
        context = zmq.Context()
        frontend = context.socket(zmq.REP)
        frontend.bind('tcp://*:5525')

        global SERVER_RUNNING
        SERVER_RUNNING = True

        while SERVER_RUNNING:
            message = frontend.recv()
            filepath = resolver.uri_to_filepath(message)

            print("Handled request %s -> %s" % (message, filepath))
            frontend.send(filepath)

        frontend.close()
        context.term()


#server = ServerTask()
#server.start()
#server.join()

createServer()
#s = raw_input()
#if s:
    #closeServer()
