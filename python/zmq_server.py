
import time
import zmq

import sys
import threading

import Tkinter
import tkMessageBox

import sys
#sys.path.insert(0, './python/')

from uri_resolver import resolver

ZMQ_PORT = 5555
SERVER_RUNNING = False

class uri_resolver_exception(Exception):
    pass

def launchServer():

    # Create ZMQ context
    context = zmq.Context()

    # Create open socket
    try:
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:%s" % ZMQ_PORT)
        print("Opened ZMQ Server!")
    except zmq.error.ZMQError:

        # Debug Log
        raise uri_resolver_exception("Address already in use!")

        # Early exit, address already in use
        return

    global SERVER_RUNNING
    SERVER_RUNNING = True

    # Listen for client requests
    try:
        print("ZMQ Server listening!")
        while SERVER_RUNNING:
            # Wait for next message
            message = socket.recv()

            print("Received message: %s" % message)

            # Convert incoming sgtk template to absolute path
            filepath = resolver.uri_to_filepath(message)

            #filepath = filepath.encode('utf-8')

            #If the path cannot be resolved, show dialog warning
            if (filepath == "NOT_FOUND"):
                root = Tkinter.Tk()
                root.update()
                root.withdraw()
                tkMessageBox.showwarning("Warning","The path: \n %s \ncannot be resolved" % message)
                root.update()
            else:
                print("Resolved path: %s" % filepath)

            # Send back resolved path
            filepath += '\0'
            socket.send(filepath)
            # Debug Log
            print("Handled request %s -> %s" % (message, filepath))

    except KeyboardInterrupt:
        raise uri_resolver_exception("Keyboard has interrupted server!")
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

    print("Closed ZMQ Server!")

# Handle server loop to restart when failure
def StartServerManager():
    print("Starting Server Manager!")

    shouldServerRestart = True
    try:
        while (shouldServerRestart):
            print(" - Launching server!")
            launchServer()
    except uri_resolver_exception as e:
        print("Server manager has caught exception: [%s]" % str(e))
    print("Stopping Server Manager!")

StartServerManager()
