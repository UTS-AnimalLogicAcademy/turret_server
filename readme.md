# turret_server
The **turret_server** runs in the background on workstation computers, waiting to receive turret uri queries from clients extending [turret_lib](https://github.com/UTS-AnimalLogicAcademy/turret_lib), ready to convert and respond with the appropriate file path. We run turret as a linux service on each artist work station. This helps to lower latency and decentralize hosting requirements. 

## Building
We use the [rez](https://github.com/nerdvegas/rez) build system at utsala, with the correct pacakge requirements, building this with rez should work straight out of the box.

Outside of rez, having the required software installed and correctly located in the `PATH` and `PYTHONPATH` environment variables should suffice.

### Requirements
 * [turret_resolver](https://github.com/UTS-AnimalLogicAcademy/turret_resolver)
 * pyzmq-16.0.3
 * Python 3 - for asyncio

## Notes
 * Projects are correctly setup in Shotgun, and configured with a shared toolkit core (https://support.shotgunsoftware.com/hc/en-us/articles/219040468)
 * Currently default file paths for logs assume a Unix platform, however in theory the code should work on Windows too

## Usage
To launch a threaded Turret server, run the [`turret-server`](https://github.com/UTS-AnimalLogicAcademy/turret_server/blob/master/bin/turret-server) executable

This launches a PyZMQ server that listens for queries from Turret clients, and delegates [turret_resolver](https://github.com/UTS-AnimalLogicAcademy/turret_resolver) fetches to one of 12 asynchronous workers. Interaction with the Shotgun API through turret_resolver is performed in its own process, allowing each process to have the CPU resources necessary, while still allowing the server to delegate to and receive responses from workers while they idle.

Sending a query which contains the word `KILL` to the turret server will signal the server to terminate.

At the Animal Logic Academy we run a turret server on each machine as a service that starts when the user logs in. As such, each machine handles its own resolving.

## Contributing
We use turret across almost every aspect of our USD pipeline and are constantly fixing bugs and finding time to improve turret more and more. We are however, very open to external pull-requests, and growing turret into a more versatile and robust piece of software with your help. Feel free to get in contact directly or through these GitHub repos. We'd love to talk! 

