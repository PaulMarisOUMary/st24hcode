SRC = mcastsocket.c
CC ?= gcc
CFLAGS += -Wall -Os

APP1 = udp_multicast_client_minimalist_version

all:
	$(CC) -o $(APP1) $(APP1).c $(SRC) $(CFLAGS)

.PHONY: clean

clean:
	rm -f $(APP1)
