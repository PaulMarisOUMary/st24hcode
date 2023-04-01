//
// Example for the env variable:
// $> export MCAST="224.1.1.1:5007"
//

// TODO test the WIN32 version
#ifdef _WIN32
	#include <Winsock2.h> // before Windows.h, else Winsock 1 conflict
	#include <Ws2tcpip.h> // needed for ip_mreq definition for multicast
	#include <Windows.h>
#else
	#include <sys/socket.h>
	#include <arpa/inet.h>
#endif

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "mcastsocket.h"

// TODO Implement env var
#define MCAST_ENV_NAME "MCAST"
#define MCAST_GROUP_DEFAULT "224.1.1.1"
#define MCAST_PORT_DEFAULT 5007

// TODO adjust below parameter values
#define MCAST_TTL 2 // see https://www.tldp.org/HOWTO/Multicast-HOWTO-6.html
#define MCAST_ALL_GROUPS 0
//#define MCAST_ALL_GROUPS 1

#define CLIENT_DEFAULT_TIMEOUT_SEC 5


// TODO better manage these globals
char group[INET_ADDRSTRLEN];
int port;
struct sockaddr_in addr; // Only for the server

#define DEBUG 0

void mcast_set_group_and_port(void)
{
	// Check the env var
	char *mcast_env = getenv(MCAST_ENV_NAME);
	if (mcast_env != NULL) { // analyze the env var
		// split ip and port
		char *ptr = strtok(mcast_env, ":");
		if (ptr == NULL)
			goto default_conf;

		// check the ip address
		struct sockaddr_in sa;
		int ret = inet_pton(AF_INET, ptr, &(sa.sin_addr));
		if (ret != 1)
			goto default_conf;

		// get the port
		ptr = strtok(NULL, ":");
		if (ptr == NULL)
			goto default_conf;

		int n = sscanf(ptr, "%d", &port);
		if (n != 1)
			goto default_conf;

		inet_ntop(AF_INET, &(sa.sin_addr), group, sizeof(group));

		// the env var is perfect, go out then...
		goto out;

	}

default_conf:
	printf("warning \"%s\" env var not defined or not correct, use default address \"%s:%d\"\n",
			MCAST_ENV_NAME, MCAST_GROUP_DEFAULT, MCAST_PORT_DEFAULT);
	snprintf(group, sizeof(group), "%s", MCAST_GROUP_DEFAULT);
	port = MCAST_PORT_DEFAULT;

out:
	return;
}

#ifdef _WIN32
bool set_win32_socket_api_version(void)
{
	// Initialize Windows Socket API with given VERSION.
	WSADATA wsaData;
	#define WVERSIONREQUIRED 0x0101
	if (WSAStartup(WVERSIONREQUIRED, &wsaData)) {
		printf("Error calling WSAStartup()\n");
		return false;
	}
	return true;
}
#endif

bool mcastserver_init(int *server_fd)
{
	mcast_set_group_and_port();

#ifdef _WIN32
	if (set_win32_socket_api_version() == false) {
		return false;
#endif

	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd < 0) {
		printf("Error calling socket()\n");
		return false;
	}

	// prepare the destination address
	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = inet_addr(group);
	addr.sin_port = htons(port);

   *server_fd = fd;

	if (DEBUG)
		printf("%s(): %s:%d ready\n", __func__, group, port);

	return true;
}

void mcastserver_sendto(int server_fd, void *byte_stream, int size)
{
	ssize_t nbytes;

	nbytes = sendto(server_fd, byte_stream, size, 0, (struct sockaddr *) &addr, sizeof(addr));
	if (nbytes < 0)
		printf("%s(): Error calling sendto()\n", __func__);

	if (DEBUG)
		printf("%s(): %i sent bytes\n", __func__, (int)nbytes);
}

bool mcastclient_init(int *client_fd)
{
	struct timeval timeout;
	timeout.tv_sec = CLIENT_DEFAULT_TIMEOUT_SEC;
	timeout.tv_usec = 0;

	mcast_set_group_and_port();

#ifdef _WIN32
	if (set_win32_socket_api_version() == false) {
		return false;
#endif

	int fd = socket(AF_INET, SOCK_DGRAM, 0);
	if (fd < 0) {
		printf("Error calling socket()\n");
		return false;
	}

	// allow multiple sockets to use the same PORT number
	u_int yes = 1;
	if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (char*) &yes, sizeof(yes)) < 0) {
	   printf("Error calling setsockopt(), Reusing ADDR failed\n");
	   return false;
	}

	// set up destination address
	// TODO manage MCAST_ALL_GROUPS
	struct sockaddr_in addr;
	memset(&addr, 0, sizeof(addr));
	addr.sin_family = AF_INET;
	addr.sin_addr.s_addr = htonl(INADDR_ANY); // differs from sender
	addr.sin_port = htons(port);

	// bind to receive address
	if (bind(fd, (struct sockaddr*) &addr, sizeof(addr)) < 0) {
		printf("Error calling bind()\n");
		return false;
	}

	// use setsockopt() to request that the kernel join a multicast group
	struct ip_mreq mreq;
	mreq.imr_multiaddr.s_addr = inet_addr(group);
	mreq.imr_interface.s_addr = htonl(INADDR_ANY);
	if (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, (char*) &mreq, sizeof(mreq)) < 0) {
		printf("Error calling setsockopt()\n");
		return false;
	}

	if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
		printf("Error calling setsockopt() for setting the timeout\n");
		return false;
	}

	*client_fd = fd;

	if (DEBUG)
		printf("%s(): %s:%d ready\n", __func__, group, port);

	return true;
}

bool mcastclient_recv(int client_fd, void *byte_stream, int size)
{
	ssize_t nbytes;
	bool ret = true;

	nbytes = recv(client_fd, byte_stream, size, 0);
	if (nbytes < 0) {
		ret = false;
		printf("%s(): Error calling recv (errno %d), probably a socket timeout, please retry...\n",
				__func__, errno);
	}

	if (DEBUG)
		printf("%s(): %i received bytes\n", __func__, (int)nbytes);

	return ret;
}
