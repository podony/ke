#pragma once
// Minimal zmq.h stub: params.cc never constructs LogState, so only
// declarations are needed (LogState is header-only, unused).
#define ZMQ_PUSH 8
#define ZMQ_LINGER 17
void* zmq_ctx_new(void);
void zmq_ctx_destroy(void* context);
void* zmq_socket(void* context, int type);
int zmq_setsockopt(void* socket, int option, const void* value, unsigned int len);
int zmq_connect(void* socket, const char* endpoint);
int zmq_close(void* socket);
