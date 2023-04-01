#ifndef RACEDATA_H
#define RACEDATA_H

#include <stdint.h> /* for uint32_t like types */

#define MAX_CARS 16 /* IMPORTANT always send MAX_CARS data even if some cars are not used */

#define CAR_POSITION_UNDEF MAX_CARS

#define CAR_STATUS_IN_RACE     96 /* Car is running */
#define CAR_STATUS_RUNWAY_EXIT 97 /* Center of the car is out of the track */
#define CAR_STATUS_PIT_STOP    98 /* Car is in pit stop, Not used */
#define CAR_STATUS_OUT_OF_RACE 99 /* Car/Aruco is not detected by server for this raceData packet */
#define CAR_STATUS_LAST CAR_STATUS_OUT_OF_RACE // Do no forget to update this one when adding more status


#define RACEDATA_STATUS_STOPPED 0  /* Race stopped */
#define RACEDATA_STATUS_STARTED 1  /* Race started */
#define RACEDATA_STATUS_SLOW    2  /* Slow speed required 25% */

struct Car {
	uint8_t status; /* car status, see CAR_STATUS_* upper */
	uint8_t position;  /* car race position */
	uint16_t orientation; /* car orientation in degree */
	float x; /* in pixel, only integer part used */
	float y; /* in pixel, only integer part used */
}__attribute__((packed)); // 1+1+2+4+4 = 12 bytes packed

struct RaceData {
	uint8_t status; /* global race status, see RACEDATA_STATUS_* upper  */
	uint32_t counter; /* incremental counter, +1 for each RaceData packet sent by server */
	uint64_t timestamp; /* server time of the RaceData, in nanosecond */
	struct Car cars[MAX_CARS]; /* Cars information */
}__attribute__((packed)); // 1+4+8+16x12 = 205 bytes packed

#endif /* RACEDATA_H */
