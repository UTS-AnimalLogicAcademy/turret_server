#
# Copyright 2019 University of Technology, Sydney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#   * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
#     the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import time
import logging
import sys
import traceback
import asyncio
import concurrent.futures

from optparse import OptionParser

import zmq
import zmq.asyncio

from turret import resolver


TURRET_LOG_LOCATION = '/usr/tmp/turret-server/log'
ZMQ_WORKERS = 12
ZMQ_PORT = 5555
ZMQ_URL = "tcp://*:%s" % ZMQ_PORT
SERVER_RUNNING = False
WORKER_URL = "inproc://workers"
SHOULD_LOG = True
DEBUG_LOG = False

LOGGER = None


class turret_server_exception(Exception):
    """

    """
    pass


def get_logger():
    """
    Returns:
        Python logger
    """
    try:
        os.makedirs(TURRET_LOG_LOCATION)
    except OSError:
        pass

    localtime = time.localtime()
    log_prefix = time.strftime('%d_%b_%Y_%H:%M:%S', localtime)
    log_path = '%s/%s_turretServer.log' % (TURRET_LOG_LOCATION, log_prefix)

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('turret-server')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger


async def process_socket(a_socket, executor, workerIdx=0):
    """
    Args:
        a_socket:
        workerIdx:
    Returns:
        None
    Raises:
        turret_server_exception
    """
    # Wait until worker has message to resolve
    loop = asyncio.get_event_loop()
    while True:
        try:
            #print("Waiting for message - %s" % workerIdx)
            message_recv = await a_socket.recv()
            #print("Received message - %s" % workerIdx)
            message = message_recv.decode()
        except zmq.ZMQError as e:
            if e.errno == zmq.EAGAIN:
                pass
            else:
                raise e
        else:
            filepath = ""
            if "KILL" in message:
                a_socket.send_string("RECEIVED")
                raise turret_server_exception("Server received kill instruction")

            for retry in range(0, 10):
                try:
                    filepath = await loop.run_in_executor(executor,resolver.uri_to_filepath,message)
                    if filepath == None:
                        continue
                    break
                except Exception as e:
                    filepath = ''
                    LOGGER.info(str(e))
                    continue

            # Send back resolved path
            filepath += '\0'
            a_socket.send_string(filepath)
            LOGGER.info("received: %s\nsent: %s\n" % (message, filepath))


async def worker_handle(workerURL, workerIdx, executor, context=None):
    """

    Args:
        workerURL:
        workerIdx:
        context:

    Returns:

    """
    # Get ref to specified context
    context = context or zmq.asyncio.Context.instance()

    # Socket to talk to dispatcher
    socket = context.socket(zmq.REP)

    socket.connect(workerURL)

    LOGGER.info("Started worker thread - %s" % workerIdx)

    try: 
        # while True:
        await process_socket(socket, executor, workerIdx)

    except turret_server_exception as e:
        raise e
    except Exception as e:
        LOGGER.info("Caught exception: [%s]" % e)
        LOGGER.info(traceback.format_exc())
        raise
        LOGGER.info("Caught exception: [%s]" % e)
        LOGGER.info(traceback.format_exc())

    LOGGER.info("Worker thread has stopped")

async def setup_proxy(clients, workers):
    # Ensure worker threads are running
    LOGGER.info("Setup ZMQ Proxy")
    await asyncio.to_thread(zmq.proxy, clients, workers)
    

def launch_threaded_server():
    """

    Returns:

    """

    LOGGER.info("Launching threaded server")

    # Create ZMQ context
    context = zmq.asyncio.Context.instance()

    # Socket to talk to resolver clients
    try:
        clients = context.socket(zmq.ROUTER)
        clients.bind(ZMQ_URL)

        # Socket to talk to workers
        workers = context.socket(zmq.DEALER)
        workers.bind(WORKER_URL)

        with concurrent.futures.ProcessPoolExecutor() as executor:

            asyncio.run(asyncio.wait([worker_handle(WORKER_URL,x,executor) for x in range(ZMQ_WORKERS)] + [setup_proxy(clients, workers)]))
        

    except zmq.error.ZMQError:
        # Debug Log
        raise turret_server_exception("ZMQ Server address already in use.")

        # Early exit, address already in use
        return

    except turret_server_exception as e:
        print("pepe")
        # Cleanup
        clients.close()
        workers.close()
        context.term()
        LOGGER.info("Closed server.")
        raise turret_server_exception(e)

    except KeyboardInterrupt:
        # Cleanup
        clients.close()
        workers.close()
        context.term()
        LOGGER.info("Closed server.")
        raise turret_server_exception("Keyboard has interrupted server.")


def launch_simple_server():
    """

    Returns:

    """
    LOGGER.info("Launching simple server")


    # Create ZMQ context
    context = zmq.Context()

    context.setsockopt(zmq.RCVHWM, 5000000)
    context.setsockopt(zmq.SNDHWM, 5000000)
    context.setsockopt(zmq.SNDTIMEO, 50000)
    context.setsockopt(zmq.RCVTIMEO, 50000)

    while True:
        socket = context.socket(zmq.REP)
        try:
            socket.bind(ZMQ_URL)
        except zmq.error.ZMQError:
            raise turret_server_exception("ZMQ Server address already in use.")

        # Listen for client requests
        try:
            process_socket(socket)

        except KeyboardInterrupt:
            raise turret_server_exception("Keyboard has interrupted server.")
        except turret_server_exception as e:
            raise turret_server_exception(e)
        except Exception as e:
            print("Caught exception:", e)

        finally:
            socket.unbind(ZMQ_URL)
            socket.close()


# Handle server loop to restart when failure
def start_server_manager(isThreaded):
    """

    Args:
        isThreaded:

    Returns:

    """


    try:
        while True:
            if isThreaded:
                # this will perform SG authentication, to avoid multiple workers trying to do it in parallel
                resolver.authenticate()
                launch_threaded_server()
            else:
                launch_simple_server()

    except turret_server_exception as e:
        print("Server manager has caught exception: [%s]" % str(e))


def main():
    p = OptionParser(usage="%prog arg1 [options]")
    p.add_option("-t", "--threaded", dest="threaded", default=False, action="store_true")
    (opts, args) = p.parse_args(sys.argv[1:])

    global LOGGER
    LOGGER = get_logger()

    start_server_manager(opts.threaded)
    


if __name__ == "__main__":
    main()
