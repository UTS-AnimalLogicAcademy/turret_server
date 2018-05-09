#! /usr/bin/python

import sys
import os, os.path

from optparse import OptionParser

import logging
import time

import threading

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

class uri_resolver_exception(Exception):
    pass

def serverLog(a_msg):
    if SHOULD_LOG:
        if a_msg != None:
            print("[ZMQ Server] " + a_msg + "\n")

def mainServerFunctionality(a_socket, workerIdx = 0):
    # Wait until worker has message to resolve
    message = a_socket.recv()

    filepath = ""
    retry = -1

    if "KILL" in message:
        a_socket.send("RECEIVED")
        raise uri_resolver_exception("Server received kill instruction")
        return

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
    a_socket.send(filepath)

def workerHandle(workerURL, workerIdx, context=None):
    # Get ref to specified context
    context = context or zmq.Context.instance()

    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)

    socket.connect(workerURL)

    serverLog("Started worker thread")

    try: 
        while True:
            mainServerFunctionality(socket, workerIdx)

    except uri_resolver_exception as e:
        raise e
    except Exception as e:
        serverLog("Caught exception: [%s]" % e)
        raise

    serverLog("Worker thread has stopped")

def workerRoutine(workerURL, workerIdx, context=None):
    while True:
        workerHandle(workerURL, workerIdx, context)

def launchThreadedServer():

    serverLog("Launching threaded server")

    # Create ZMQ context
    context = zmq.Context.instance()

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
    except uri_resolver_exception as e:
        print "pepe"
        # Cleanup
        clients.close()
        workers.close()
        context.term()

        serverLog("Closed server.")
        raise uri_resolver_exception(e)
    except KeyboardInterrupt:
        # Cleanup
        clients.close()
        workers.close()
        context.term()

        serverLog("Closed server.")
        raise uri_resolver_exception("Keyboard has interrupted server.")

def launchSimpleServer():

    serverLog("Launching simple server")

    # Create ZMQ context
    context = zmq.Context()

    context.setsockopt(zmq.RCVHWM, 5000000)
    context.setsockopt(zmq.SNDHWM, 5000000)
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

    # Listen for client requests
    try:
        while True:
            mainServerFunctionality(socket)

    except KeyboardInterrupt:
        raise uri_resolver_exception("Keyboard has interrupted server.")
    except uri_resolver_exception as e:
        raise uri_resolver_exception(e)
    except Exception as e:
        print("Caught exception: [%s]" % e)

    # Close server
    socket.close()

# Handle server loop to restart when failure
def StartServerManager(isThreaded):
    try:
        while True:
            if isThreaded:
                launchThreadedServer()
            else:
                launchSimpleServer()
            
    except uri_resolver_exception as e:
        print("Server manager has caught exception: [%s]" % str(e))

def main():
    # Setup option parser
    p = OptionParser(usage="%prog arg1 [options]")

    #p.add_option("-p", "--port", dest="port", default=DEFAULT_PORT, action="store", type="int")
    #p.add_option("-m", "--message", dest="message", default=DEFAULT_MSG, action="store")
    #p.add_option("-n", "--numMessages", dest="numMessages", default=DEFAULT_NUM_MESSAGES, action="store", type="int")
    #p.add_option("-t", "--numThreads", dest="numThreads", default=DEFAULT_NUM_THREADS, action="store", type="int")
    p.add_option("-t", "--threaded", dest="threaded", default=False, action="store_true")
    
    # Run option parser
    (opts, args) = p.parse_args(sys.argv[1:])
    StartServerManager(opts.threaded)

#main()
StartServerManager(False)
#launchSimpleServer()