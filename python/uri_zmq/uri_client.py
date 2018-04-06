import zmq
import sys

def createClient():
    context = zmq.Context()
    #  Socket to talk to server
    print("Connecting to uri resolver server...")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    # Get user input for testing
    #tank_query = raw_input("Enter tank query: ")

    query = "tank:/maya_publish_asset_cache_usd?Asset=building01&Step=model&Task=model&version=latest"
    if(len(sys.argv) > 1):
        query = sys.argv[1]

    tank_query = query
    tq_buffer = tank_query.encode("utf8")

    # Send tank path
    socket.send(tq_buffer)

    print("Sent: %s" % tq_buffer)

    # Receive absolute path
    receivedPath = socket.recv()

    print("Received: %s" % receivedPath)

    socket.close()

createClient()
