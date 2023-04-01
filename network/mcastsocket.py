# UDP MultiCast part greatly inspired from
# https://stackoverflow.com/questions/603852/how-do-you-udp-multicast-in-python#1794373
#
# Example for the env variable:
# $> export MCAST="224.1.1.1:5007"
#
# For Windows only, set the network interface IP env variable (no ""):
# $> set NETWORK_INTERFACE=10.201.21.74
#

import platform
import socket
import struct
import os

debug = False

MCAST_ENV_NAME = "MCAST"
MCAST_GROUP_DEFAULT = "224.1.1.1"
MCAST_PORT_DEFAULT = 5007

# Windows requires the network interface IP
NETWORK_INTERFACE_ENV_NAME = "NETWORK_INTERFACE"
NETWORK_INTERFACE_DEFAULT_IP = "127.0.0.1"

# TODO adjust below parameter values
MCAST_TTL = 2 # see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html
IS_ALL_GROUPS = False
#IS_ALL_GROUPS = True
MCAST_DATA_SIZE_DEFAULT = 256

CLIENT_DEFAULT_TIMEOUT_SEC = 5


def mcast_get_group_and_port():
    mcast_group = MCAST_GROUP_DEFAULT
    mcast_port = MCAST_PORT_DEFAULT

    # Try to get the port from the env
    mcast_env = os.getenv(MCAST_ENV_NAME)
    if debug:
        print("__mcast_get_group_and_port(): mcast_env", mcast_env)

    if mcast_env == None:
        print("warning \"{}\" env var not defined, use default address \"{}:{}\""
            .format(MCAST_ENV_NAME, MCAST_GROUP_DEFAULT, MCAST_PORT_DEFAULT))
    else:
        group, port = mcast_env.split(":")
        if port.isdigit():
            mcast_port = int(port)
            mcast_group = group # TODO we may check group too
        else:
            print("mcast socket: warning: \"{}\" env var is not correct, use default address \"{}:{}\""
            .format(MCAST_ENV_NAME, MCAST_GROUP_DEFAULT, MCAST_PORT_DEFAULT))

    return mcast_group, mcast_port


def mcast_get_network_interface():
    network_interface = NETWORK_INTERFACE_DEFAULT_IP

    # Try to get the network interface from the env
    network_interface_env = os.getenv(NETWORK_INTERFACE_ENV_NAME)
    if debug:
        print("mcast_get_network_interface(): network_interface_env", network_interface_env)

    if network_interface_env == None:
        print("warning \"{}\" env var not defined, use default address \"{}\""
            .format(NETWORK_INTERFACE_ENV_NAME, NETWORK_INTERFACE_DEFAULT_IP))
    else:
        network_interface = network_interface_env # TODO we may check group too

    return network_interface


class MCastServer:
    def __init__(self) -> None:
        self.mcast_group, self.mcast_port = mcast_get_group_and_port()
        if debug:
            print("MCastServer(): {}:{}".format(self.mcast_group, self.mcast_port))

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MCAST_TTL)

    def sendto(self, byte_stream: bytes):
        self.sock.sendto(byte_stream, (self.mcast_group, self.mcast_port))


class MCastClient:
    def __init__(self, timeout_sec=CLIENT_DEFAULT_TIMEOUT_SEC) -> None:
        self.mcast_group, self.mcast_port = mcast_get_group_and_port()
        if debug:
            print("MCastClient(): {}:{}".format(self.mcast_group, self.mcast_port))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        if platform.system() == "Windows":
            self.network_interface = mcast_get_network_interface()
            ip_bind = self.network_interface
        else:
            ip_bind = self.mcast_group

        if IS_ALL_GROUPS:
            sock.bind(("", self.mcast_port)) # on this port, receives ALL multicast groups
        else:
            sock.bind((ip_bind, self.mcast_port)) # on this port, listen ONLY to MCAST_GRP

        if platform.system() == "Windows":
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.network_interface))
            mreq = struct.pack("4s4s", socket.inet_aton(self.mcast_group),
                               socket.inet_aton(self.network_interface))
        else:
            mreq = struct.pack("4sl", socket.inet_aton(self.mcast_group), socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        sock.settimeout(timeout_sec)

        self.sock = sock

    def recv(self) -> bytes:
        try:
            byte_stream = self.sock.recv(MCAST_DATA_SIZE_DEFAULT)
        except OSError as err:
            print("Warning: socket {}: no data received, please retry...".format(err))
            byte_stream = None
        return byte_stream

    # Closing the socket helps flushing it
    def flush_and_close(self) -> None:
        self.sock.close()
