# Network

## Short presentation
The network part is based here on **UDP multicast sockets**: a server sends the same data to a group of clients.
Note that *User Datagram Protocol* (UDP) is a connection-less, unreliable, datagram protocol ie. clients may not
received some datagrams and lost datagrams will not be re-sent by the server. It is not really an issue for
targeted "real time" use cases.

Please have a look to source code examples shortly presented in the next chapter.


## Directory content
This "network" directory contains:
* Helpers
    * racedata.*
    * mcastsocket.*
* Examples using above helpers
    * udp_multicast_client_minimalist_version.*
    * udp_multicast_client.py (python only)
* Other files
    * Makefile: only usefull to build C examples

**IMPORTANT** All files are available for both Python and C languages.


## Set the network address and port
```bash
# Example for the env variable
$> export MCAST="224.1.1.2:5008"
# Start then your preferred example
python3 udp_multicast_client_minimalist_version.py
# or
./udp_multicast_client_minimalist_version
# or
...
```
