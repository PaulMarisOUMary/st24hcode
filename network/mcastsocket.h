#ifndef MCASTSOCKET_H
#define MCASTSOCKET_H
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>

// return false in case of error
bool mcastserver_init(int *server_fd);
void mcastserver_sendto(int server_fd, void *byte_stream, int size);

// return false in case of error
bool mcastclient_init(int *client_fd);
bool mcastclient_recv(int client_fd, void *byte_stream, int size);

#ifdef __cplusplus
}
#endif
#endif /* MCASTSOCKET_H */
