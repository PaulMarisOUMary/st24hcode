#include <stdio.h>

#include "racedata.h"
#include "mcastsocket.h"

int main(void)
{
	// Network part
	int client_fd;
	if (mcastclient_init(&client_fd) == false) {
		printf("Error calling mcastclient_init()\n");
		return 1;
	}

	// Data part
	int car_id = 1;                                 // <----- PUT HERE YOUR CAR ID
	struct RaceData racedata;
	struct Car *car = &racedata.cars[car_id];

	while (1) {
		// Get data from the udp multicast socket and unpack them
		if (!mcastclient_recv(client_fd, &racedata, sizeof(racedata)))
			continue;

		printf("car status %i, position %i, orientation %i°, x %f, y %f, race status %i counter %u, timestamp %lu\n",
				car->status, car->position, car->orientation, car->x, car->y,
				racedata.status, racedata.counter, racedata.timestamp);
	}

	return 0;
}
