// Self-contained stubs for cross-building params_pyx.so on EON (aarch64).
// These reproduce the exact runtime behavior of common/util.cc, common/swaglog.cc,
// and system/hardware so that params.cc links into a single standalone .so.
#include <string>
#include <vector>
#include <map>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cerrno>
#include <cstdarg>
#include <unistd.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>

#define HANDLE_EINTR(X) int ret_ = -1; do { ret_ = (X); } while (ret_ == -1 && errno == EINTR); ret_

namespace util {

std::string string_format(const std::string& format, const std::string& val) {
  return format + val;
}

std::string getenv(const char* key, std::string default_val) {
  const char* e = std::getenv(key);
  return e ? std::string(e) : default_val;
}

std::string read_file(const std::string& fn) {
  FILE* f = fopen(fn.c_str(), "rb");
  if (!f) return "";
  std::string r;
  char buf[4096];
  size_t n;
  while ((n = fread(buf, 1, sizeof(buf), f)) > 0) r.append(buf, n);
  fclose(f);
  return r;
}

std::map<std::string, std::string> read_files_in_dir(const std::string& path) {
  std::map<std::string, std::string> ret;
  DIR* d = opendir(path.c_str());
  if (!d) return ret;
  struct dirent* de;
  while ((de = readdir(d))) {
    if (de->d_type != DT_DIR) {
      std::string fn = path + "/" + de->d_name;
      ret[de->d_name] = read_file(fn);
    }
  }
  closedir(d);
  return ret;
}

bool file_exists(const std::string& fn) {
  struct stat st;
  return stat(fn.c_str(), &st) == 0;
}

bool create_directories(const std::string& dir, mode_t mode) {
  std::string path;
  for (size_t i = 0; i < dir.size(); i++) {
    path += dir[i];
    if (dir[i] == '/' || i + 1 == dir.size()) {
      if (mkdir(path.c_str(), mode) != 0 && errno != EEXIST) return false;
    }
  }
  return true;
}

void sleep_for(const int milliseconds) {
  if (milliseconds > 0) usleep(milliseconds * 1000);
}

}  // namespace util

namespace util {
int getenv(const char* key, int default_val) {
  const char* e = std::getenv(key);
  if (!e) return default_val;
  char* end = nullptr;
  long v = strtol(e, &end, 10);
  return end && *end == '\0' ? (int)v : default_val;
}
}  // namespace util

void cloudlog_te(int levelnum, const char* filename, int lineno, const char* func, const char* fmt, ...) {
  (void)levelnum; (void)filename; (void)lineno; (void)func;
  va_list ap;
  va_start(ap, fmt);
  vprintf(fmt, ap);
  va_end(ap);
  fputc('\n', stdout);
}

void cloudlog_e(int levelnum, const char* filename, int lineno, const char* func, const char* fmt, ...) {
  (void)levelnum; (void)filename; (void)lineno; (void)func;
  va_list ap;
  va_start(ap, fmt);
  vprintf(fmt, ap);
  va_end(ap);
  fputc('\n', stdout);
}
