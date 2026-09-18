#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include "common/swaglog.h"

#include <cassert>
#include <cstring>
#include <mutex>
#include <string>

#include <zmq.h>

#include "common/util.h"
#include "common/version.h"
#include "system/hardware/hw.h"

class SwaglogState : public LogState {
 public:
  SwaglogState() : LogState("ipc:///tmp/logmessage") {}

  bool initialized = false;

  inline void initialize() {
    print_level = CLOUDLOG_WARNING;
    const char* print_lvl = getenv("LOGPRINT");
    if (print_lvl) {
      if (strcmp(print_lvl, "debug") == 0) {
        print_level = CLOUDLOG_DEBUG;
      } else if (strcmp(print_lvl, "info") == 0) {
        print_level = CLOUDLOG_INFO;
      }
    }

    char* dongle_id = getenv("DONGLE_ID");
    if (dongle_id) {
      // just for context, not logged here
    }
    char* daemon_name = getenv("MANAGER_DAEMON");
    if (daemon_name) {
      // just for context, not logged here
    }

    initialized = true;
  }
};

static SwaglogState s = {};
bool LOG_TIMESTAMPS = getenv("LOG_TIMESTAMPS") != nullptr;

static void log(int levelnum, const char* filename, const char* msg) {
  if (levelnum >= s.print_level) {
    printf("%s: %s\n", filename, msg);
  }
  // Send a simple text line over ZMQ for the swaglog daemon
  char line[8192];
  snprintf(line, sizeof(line), "%d|%s", levelnum, msg);
  zmq_send(s.sock, line, strlen(line), ZMQ_NOBLOCK);
}

static void cloudlog_common(int levelnum, bool is_timestamp, const char* filename, const char* func,
                            const char* fmt, va_list args) {
  char* msg_buf = nullptr;
  int ret = vasprintf(&msg_buf, fmt, args);
  if (ret <= 0 || !msg_buf) return;

  std::lock_guard lk(s.lock);

  if (!s.initialized) s.initialize();

  if (is_timestamp) {
    char ts_buf[8192];
    snprintf(ts_buf, sizeof(ts_buf), "[%lu] %s", (unsigned long)nanos_since_boot(), msg_buf);
    log(levelnum, filename, ts_buf);
  } else {
    log(levelnum, filename, msg_buf);
  }
  free(msg_buf);
}

void cloudlog_e(int levelnum, const char* filename, int lineno, const char* func,
                const char* fmt, ...) {
  va_list args;
  va_start(args, fmt);
  cloudlog_common(levelnum, false, filename, func, fmt, args);
  va_end(args);
}

void cloudlog_te(int levelnum, const char* filename, int lineno, const char* func,
                 const char* fmt, ...) {
  if (!LOG_TIMESTAMPS) return;
  va_list args;
  va_start(args, fmt);
  cloudlog_common(levelnum, true, filename, func, fmt, args);
  va_end(args);
}

void cloudlog_te(int levelnum, const char* filename, int lineno, const char* func,
                 uint32_t frame_id, const char* fmt, ...) {
  if (!LOG_TIMESTAMPS) return;
  char* msg_buf = nullptr;
  va_list args;
  va_start(args, fmt);
  int ret = vasprintf(&msg_buf, fmt, args);
  va_end(args);
  if (ret <= 0 || !msg_buf) return;

  std::lock_guard lk(s.lock);
  if (!s.initialized) s.initialize();

  char ts_buf[8192];
  snprintf(ts_buf, sizeof(ts_buf), "[%lu|%u] %s", (unsigned long)nanos_since_boot(), frame_id, msg_buf);
  log(levelnum, filename, ts_buf);
  free(msg_buf);
}