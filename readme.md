# turret_server
**turret_server** is the backbone of all other turret plugins. The server runs in the background on workstation computers, waiting to receive turret uri queries, ready to convert and respond with the appropriate file path. We run turret as a linux service on each artist work station. This helps to lower latency and decentralize hosting requirements. 

## Requirements
 * turret_resolver
 * pyzmq-16.0.3

## Notes
 * Projects are correctly setup in Shotgun, and configured with a shared toolkit core (https://support.shotgunsoftware.com/hc/en-us/articles/219040468)
 * Currently default file paths for logs assume a Unix platform, however in theory the code should work on Windows too

## Contributing
We use turret across almost every aspect of our USD pipeline and are constantly fixing bugs and finding time to improve turret more and more. We are however, very open to external pull-requests, and growing turret into a more versatile and robust piece of software with your help. Feel free to get in contact directly or through these GitHub repos. We'd love to talk! 

