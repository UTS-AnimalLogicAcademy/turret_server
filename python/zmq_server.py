#! /usr/bin/python

import os
import logging
import time
import sys
import threading
import Tkinter
import tkMessageBox
import sys

import zmq

from uri_resolver import resolver


ZMQ_LOG_LOCATION = '/tmp/tank_zmq_server/log'
ZMQ_PORT = 5555
SERVER_RUNNING = False


class uri_resolver_exception(Exception):
    pass


#def getLogger():
#    try:
#        os.makedirs(ZMQ_LOG_LOCATION)
#    except OSError:
#        pass
#
#    localtime = time.localtime()
#    log_prefix = time.strftime('%d_%b_%Y_%H:%M:%S', localtime)
#    log_path = '%s/%s_tank_zmq.log' % (ZMQ_LOG_LOCATION, log_prefix)
#
#    logging.basicConfig(level=logging.INFO)
#    logger = logging.getLogger(__name__)
#    logger.setLevel(logging.INFO)
#
#    handler = logging.FileHandler(log_path)
#    handler.setLevel(logging.INFO)
#    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#    handler.setFormatter(formatter)
#    logger.addHandler(handler)
#
#    return logger


def launchServer():

    # Create ZMQ context
    context = zmq.Context()

    context.setsockopt(zmq.RCVHWM, 100000)
    context.setsockopt(zmq.SNDHWM, 100000)
    context.setsockopt(zmq.SNDTIMEO, 50000)
    context.setsockopt(zmq.RCVTIMEO, 50000)

    # Create open socket
    try:
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % ZMQ_PORT)
        print("Opened ZMQ Server.")
    except zmq.error.ZMQError:

        # Debug Log
        raise uri_resolver_exception("ZMQ Server address already in use.")

        # Early exit, address already in use
        return

    global SERVER_RUNNING
    SERVER_RUNNING = True

    # Listen for client requests
    try:
#        logger = getLogger()
#        logger.info("ZMQ Server listening.")
        while SERVER_RUNNING:
            # Wait for next message
            message = socket.recv()

#            logger.info("zmq server received message: %s" % message)
            print("zmq server received message: %s" % message)

            # Convert incoming sgtk template to absolute path
            filepath = resolver.uri_to_filepath(message)

            #filepath = filepath.encode('utf-8')
            '''
            # Will send garbage to client when loading sets, forgo popup for now
            
            # If the path cannot be resolved, show dialog warning
            if (filepath == "NOT_FOUND"):
                root = Tkinter.Tk()
                root.update()
                root.withdraw()
                tkMessageBox.showwarning("Warning", "The path: \n %s \ncannot be resolved" % message)
                root.update()
            else:
                logger.info("zmq server resolved path: %s\n" % filepath)
            '''
            
#            logger.info("zmq server resolved path: %s\n" % filepath)
            print("zmq server resolved path: %s\n" % filepath)

            # Send back resolved path
            filepath += '\0'
            socket.send(filepath)
            # Debug Log
#            logger.info("zmq server handled request %s -> %s" % (message, filepath))
            print("zmq server handled request %s -> %s" % (message, filepath))

    except KeyboardInterrupt:
        raise uri_resolver_exception("Keyboard has interrupted server.")
    except Exception as e:
        print("Caught exception: [%s]" % e)
    #except TypeError as e:
    #    print("Caught type error [%s]" % str(e))
    #except ValueError as e:
    #    print("Caught value error [%s]" % str(e))
    #except IndexError as e:
    #    print("Caught index error [%s]" % str(e))

    # Close server
    socket.close()

    print("Closed ZMQ Server.")


# Handle server loop to restart when failure
def StartServerManager():
    print("Starting Server Manager.")

    shouldServerRestart = True
    try:
        while (shouldServerRestart):
            print(" - Launching server.")
            launchServer()
    except uri_resolver_exception as e:
        print("Server manager has caught exception: [%s]" % str(e))
    print("Stopping Server Manager.")

StartServerManager()
