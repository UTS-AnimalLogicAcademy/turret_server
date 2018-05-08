import sys
import os, os.path

from optparse import OptionParser

from threading import Thread
from time import sleep

import zmq

DEFAULT_ADDRESS = "localhost"
DEFAULT_PORT = 5555
DEFAULT_MSG = "tank:/maya_publish_asset_cache_usd?Asset=building01&Step=model&Task=model&version=latest"
DEFAULT_NUM_MESSAGES = 1
DEFAULT_NUM_THREADS = 1

SHOULD_OUTPUT = False

def logClient(a_msg):
    if SHOULD_OUTPUT:
        print(a_msg)

def createClient(a_address=DEFAULT_ADDRESS, a_port=DEFAULT_PORT, a_message=DEFAULT_MSG, a_numMessages=DEFAULT_NUM_MESSAGES):
    context = zmq.Context()
    #  Socket to talk to server
    logClient("Connecting to uri resolver server...")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://%s:%s" % (a_address, a_port))

    query = a_message

    tank_query = query
    tq_buffer = tank_query.encode("utf8")

    for i in range(a_numMessages):
        # Send tank path
        socket.send(tq_buffer)

        logClient("Sent: %s" % tq_buffer)

        # Receive absolute path
        receivedPath = socket.recv()

        logClient("Received: %s" % receivedPath)

    print("Sent %s messages" % a_numMessages)

    socket.close()


def handleClient(options):
    threads = []

    # Start all threads
    for i in range(options.numThreads):
        thread = Thread(target = createClient, args = (options.address, options.port, options.message, options.numMessages))
        thread.start()
        threads.append(thread)

    # Wait for all threads to join
    for i in range(len(threads)):
        threads[i].join()
    
    print("Finished %s threads" % options.numThreads)

def main():
    # Setup option parser
    p = OptionParser(usage="%prog arg1 [options]")

    p.add_option("-a", "--address", dest="address", default=DEFAULT_ADDRESS, action="store")
    p.add_option("-p", "--port", dest="port", default=DEFAULT_PORT, action="store", type="int")
    p.add_option("-m", "--message", dest="message", default=DEFAULT_MSG, action="store")
    p.add_option("-n", "--numMessages", dest="numMessages", default=DEFAULT_NUM_MESSAGES, action="store", type="int")
    p.add_option("-t", "--numThreads", dest="numThreads", default=DEFAULT_NUM_THREADS, action="store", type="int")
    p.add_option("-d", "--debug", dest="debug", default=False, action="store_true")
    
    # Run option parser
    (opts, args) = p.parse_args(sys.argv[1:])

    global SHOULD_OUTPUT
    SHOULD_OUTPUT = opts.debug

    handleClient(opts)

main()