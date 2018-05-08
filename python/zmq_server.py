#! /usr/bin/python

import os
import logging
import time
import sys
import threading
import sys

import zmq

from uri_resolver import resolver

ZMQ_LOG_LOCATION = '/tmp/tank_zmq_server/log'

ZMQ_WORKERS = 16
ZMQ_PORT = 5555
ZMQ_URL = "tcp://*:%s" % ZMQ_PORT

SERVER_RUNNING = False

WORKER_URL = "inproc://workers"

SHOULD_LOG = True

class uri_resolver_exception(Exception):
    pass

def serverLog(a_msg):
    if SHOULD_LOG:
        if a_msg != None:
            print("[ZMQ Server] " + a_msg + "\n")

def workerHandle(workerURL, workerIdx, context=None):
    # Get ref to specified context
    context = context or zmq.Context.instance()

    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)

    socket.connect(workerURL)

    serverLog("Started worker thread")

    try: 
        while True:
            # Wait until worker has message to resolve
            message = socket.recv()

            filepath = ""
            retry = -1

            for retry in range(0,10):
                try:
                    filepath = resolver.uri_to_filepath(message)
                    if filepath == None:
                        continue
                    break
                except Exception as e:
                    serverLog(e)
                    #time.sleep(5)
                    continue

                serverLog("Giving up")
                filepath = "###_Could_not_resolve"

            serverLog("Worker: %02d. Retries: %02d. Resolved Path: %s." % (workerIdx, retry, filepath))

            # Send back resolved path
            filepath += '\0'
            socket.send(filepath)

    except KeyboardInterrupt:
        raise uri_resolver_exception("Keyboard has interrupted server.")
    except Exception as e:
        serverLog("Caught exception: [%s]" % e)

    serverLog("Worker thread has stopped")

def workerRoutine(workerURL, workerIdx, context=None):
    while True:
        workerHandle(workerURL, workerIdx, context)

def launchServer():

    # Create ZMQ context
    context = zmq.Context.instance()

    #context.setsockopt(zmq.RCVHWM, 5000000)
    #context.setsockopt(zmq.SNDHWM, 5000000)
    #context.setsockopt(zmq.SNDTIMEO, 50000)
    #context.setsockopt(zmq.RCVTIMEO, 50000)

    # Socket to talk to resolver clients
    try:
        clients = context.socket(zmq.ROUTER)
        clients.bind(ZMQ_URL)

        # Socket to talk to workers
        workers = context.socket(zmq.DEALER)
        workers.bind(WORKER_URL)

        # Launch pool of workers
        for i in range(ZMQ_WORKERS):
            thread = threading.Thread(target=workerRoutine, args=(WORKER_URL, i,))
            thread.start()

        serverLog("Open server with %s workers." % ZMQ_WORKERS)
        
        # Link clients and workers
        zmq.proxy(clients, workers)


    except zmq.error.ZMQError:

        # Debug Log
        raise uri_resolver_exception("ZMQ Server address already in use.")

        # Early exit, address already in use
        return
    except KeyboardInterrupt:
        # Cleanup
        clients.close()
        workers.close()
        context.term()

        serverLog("Closed server.")
        raise uri_resolver_exception("Keyboard has interrupted server.")


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