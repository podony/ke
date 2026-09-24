// Minimal standalone build of common/params.cc for Termux (EON).
// Strips swaglog/util/hw.h dependencies so it compiles with only POSIX + STL.
// Keep the keys table in sync with common/params.cc.

#include "common/params.h"

#include <dirent.h>
#include <sys/file.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <stdlib.h>
#include <cstdio>
#include <sys/stat.h>
#include <sys/types.h>

#include <algorithm>
#include <csignal>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

namespace {

#define HANDLE_EINTR(x)                                        \
  ({                                                           \
    decltype(x) ret_;                                          \
    int try_cnt = 0;                                           \
    do {                                                       \
      ret_ = (x);                                              \
    } while (ret_ == -1 && errno == EINTR && try_cnt++ < 100); \
    ret_;                                                       \
  })

volatile sig_atomic_t params_do_exit = 0;
void params_sig_handler(int signal) {
  params_do_exit = 1;
}

int fsync_dir(const std::string &path) {
  int result = -1;
  int fd = HANDLE_EINTR(open(path.c_str(), O_RDONLY, 0755));
  if (fd >= 0) {
    result = fsync(fd);
    close(fd);
  }
  return result;
}

bool file_exists(const std::string &path) {
  struct stat st;
  return stat(path.c_str(), &st) == 0;
}

bool create_directories(const std::string &path, int mode) {
  std::string current;
  for (size_t i = 0; i < path.size(); i++) {
    current += path[i];
    if (path[i] == '/' || i == path.size() - 1) {
      if (current != "/" && !file_exists(current)) {
        if (mkdir(current.c_str(), mode) != 0 && errno != EEXIST) {
          return false;
        }
      }
    }
  }
  return true;
}

bool create_params_path(const std::string &param_path, const std::string &key_path) {
  if (!file_exists(param_path) && !create_directories(param_path, 0775)) {
    return false;
  }
  if (!file_exists(key_path)) {
    std::string tmp_path = param_path + "/.tmp_XXXXXX";
    char *tmp_dir = mkdtemp((char *)tmp_path.c_str());
    if (tmp_dir == NULL) {
      return false;
    }
    std::string link_path = std::string(tmp_dir) + ".link";
    if (symlink(tmp_dir, link_path.c_str()) != 0) {
      return false;
    }
    if (rename(link_path.c_str(), key_path.c_str()) != 0 && errno != EEXIST) {
      return false;
    }
  }
  return true;
}

std::string get_params_root(const std::string &prefix, const std::string &path) {
  std::string params_path = path.empty() ? std::string("/data/params") : path;
  if (!create_params_path(params_path, params_path + prefix)) {
    // Non-fatal: if /data/params cannot be created (e.g. storage not ready at
    // boot), keep returning the default path instead of throwing. Params
    // access will fail individually, but car-list build and manager start
    // must not die at import time.
    fprintf(stderr, "params: failed to ensure %s path, errno=%d (continuing non-fatal)",
            params_path.c_str(), errno);
  }
  return params_path;
}

class FileLock {
public:
  FileLock(const std::string &fn) {
    fd_ = HANDLE_EINTR(open(fn.c_str(), O_CREAT | O_RDWR, 0775));
    if (fd_ < 0 || HANDLE_EINTR(flock(fd_, LOCK_EX)) < 0) {
      // non-fatal in minimal build
    }
  }
  ~FileLock() { if (fd_ >= 0) close(fd_); }

private:
  int fd_ = -1;
};

std::string read_file(const std::string &path) {
  std::string ret;
  int fd = open(path.c_str(), O_RDONLY);
  if (fd < 0) return ret;
  char buf[4096];
  ssize_t n;
  while ((n = read(fd, buf, sizeof(buf))) > 0) {
    ret.append(buf, n);
  }
  close(fd);
  return ret;
}

std::unordered_map<std::string, uint32_t> keys = {
    {"AccessToken", PERSISTENT},
    {"ApiCache_Device", PERSISTENT},
    {"ApiCache_DriveStats", PERSISTENT},
    {"ApiCache_NavDestinations", PERSISTENT},
    {"AssistNowToken", PERSISTENT},
    {"AthenadPid", PERSISTENT},
    {"AthenadUploadQueue", PERSISTENT},
    {"CalibrationParams", PERSISTENT},
    {"CameraDebugExpGain", CLEAR_ON_MANAGER_START},
    {"CameraDebugExpTime", CLEAR_ON_MANAGER_START},
    {"CarBatteryCapacity", PERSISTENT},
    {"CarParams", PERSISTENT},
    {"CarParamsCache", CLEAR_ON_MANAGER_START},
    {"CarParamsPersistent", PERSISTENT},
    {"CarParamsPrevRoute", PERSISTENT},
    {"CarVin", PERSISTENT},
    {"CompletedTrainingVersion", PERSISTENT},
    {"ControlsReady", PERSISTENT},
    {"CurrentBootlog", PERSISTENT},
    {"CurrentRoute", PERSISTENT},
    {"DisableLogging", PERSISTENT},
    {"DisablePowerDown", PERSISTENT},
    {"DisableUpdates", PERSISTENT},
    {"DisengageOnAccelerator", PERSISTENT},
    {"DmModelInitialized", CLEAR_ON_ONROAD_TRANSITION},
    {"DoReboot", CLEAR_ON_MANAGER_START},
    {"DoShutdown", CLEAR_ON_MANAGER_START},
    {"DoUninstall", CLEAR_ON_MANAGER_START},
    {"DongleId", PERSISTENT},
    {"ExperimentalLongitudinalEnabled", PERSISTENT},
    {"ExperimentalMode", PERSISTENT},
    {"ExperimentalModeConfirmed", PERSISTENT},
    {"FirmwareQueryDone", PERSISTENT},
    {"ForcePowerDown", PERSISTENT},
    {"GitBranch", PERSISTENT},
    {"GitCommit", PERSISTENT},
    {"GitCommitDate", PERSISTENT},
    {"GitDiff", PERSISTENT},
    {"GitRemote", PERSISTENT},
    {"GithubSshKeys", PERSISTENT},
    {"GithubUsername", PERSISTENT},
    {"GsmApn", PERSISTENT},
    {"GsmMetered", PERSISTENT},
    {"GsmRoaming", PERSISTENT},
    {"HardwareSerial", PERSISTENT},
    {"HasAcceptedTerms", PERSISTENT},
    {"IMEI", PERSISTENT},
    {"InstallDate", PERSISTENT},
    {"IsDriverViewEnabled", CLEAR_ON_MANAGER_START},
    {"IsEngaged", PERSISTENT},
    {"IsLdwEnabled", PERSISTENT},
    {"IsMetric", PERSISTENT},
    {"IsOffroad", CLEAR_ON_MANAGER_START},
    {"IsOnroad", PERSISTENT},
    {"IsReleaseBranch", CLEAR_ON_MANAGER_START},
    {"IsRhdDetected", PERSISTENT},
    {"IsTakingSnapshot", CLEAR_ON_MANAGER_START},
    {"IsTestedBranch", CLEAR_ON_MANAGER_START},
    {"IsUpdateAvailable", CLEAR_ON_MANAGER_START},
    {"JoystickDebugMode", PERSISTENT},
    {"LaikadEphemerisV3", PERSISTENT},
    {"LanguageSetting", PERSISTENT},
    {"LastAthenaPingTime", CLEAR_ON_MANAGER_START},
    {"LastGPSPosition", PERSISTENT},
    {"LastManagerExitReason", CLEAR_ON_MANAGER_START},
    {"LastOffroadStatusPacket", PERSISTENT},
    {"LastPowerDropDetected", CLEAR_ON_MANAGER_START},
    {"LastSystemShutdown", CLEAR_ON_MANAGER_START},
    {"LastUpdateException", CLEAR_ON_MANAGER_START},
    {"LastUpdateTime", PERSISTENT},
    {"LiveParameters", PERSISTENT},
    {"LiveTorqueCarParams", PERSISTENT},
    {"LiveTorqueParameters", PERSISTENT},
    {"LongitudinalPersonality", PERSISTENT},
    {"NavDestination", PERSISTENT},
    {"NavDestinationWaypoints", PERSISTENT},
    {"NavSettingLeftSide", PERSISTENT},
    {"NavSettingTime24h", PERSISTENT},
    {"NavdRender", PERSISTENT},
    {"NetworkMetered", PERSISTENT},
    {"OPENPILOT_PREFIX", PERSISTENT},
    {"ObdMultiplexingChanged", PERSISTENT},
    {"ObdMultiplexingEnabled", PERSISTENT},
    {"Offroad_BadNvme", CLEAR_ON_MANAGER_START},
    {"Offroad_CarUnrecognized", PERSISTENT},
    {"Offroad_ConnectivityNeeded", CLEAR_ON_MANAGER_START},
    {"Offroad_ConnectivityNeededPrompt", CLEAR_ON_MANAGER_START},
    {"Offroad_InvalidTime", CLEAR_ON_MANAGER_START},
    {"Offroad_IsTakingSnapshot", CLEAR_ON_MANAGER_START},
    {"Offroad_NeosUpdate", CLEAR_ON_MANAGER_START},
    {"Offroad_NoFirmware", PERSISTENT},
    {"Offroad_Recalibration", PERSISTENT},
    {"Offroad_StorageMissing", CLEAR_ON_MANAGER_START},
    {"Offroad_TemperatureTooHigh", CLEAR_ON_MANAGER_START},
    {"Offroad_UnofficialHardware", CLEAR_ON_MANAGER_START},
    {"Offroad_UpdateFailed", CLEAR_ON_MANAGER_START},
    {"OpenpilotEnabledToggle", PERSISTENT},
    {"PandaHeartbeatLost", PERSISTENT},
    {"PandaLogState", PERSISTENT},
    {"PandaSignatures", CLEAR_ON_MANAGER_START},
    {"Passive", PERSISTENT},
    {"PrimeType", PERSISTENT},
    {"RecordFront", PERSISTENT},
    {"RecordFrontLock", PERSISTENT},
    {"ReplayControlsState", PERSISTENT},
    {"ShouldDoUpdate", CLEAR_ON_MANAGER_START},
    {"SnoozeUpdate", PERSISTENT},
    {"SshEnabled", PERSISTENT},
    {"SubscriberInfo", PERSISTENT},
    {"TermsVersion", PERSISTENT},
    {"TrainingVersion", PERSISTENT},
    {"UbloxAvailable", PERSISTENT},
    {"UpdateFailedCount", CLEAR_ON_MANAGER_START},
    {"UpdaterAvailableBranches", CLEAR_ON_MANAGER_START},
    {"UpdaterCurrentDescription", CLEAR_ON_MANAGER_START},
    {"UpdaterCurrentReleaseNotes", CLEAR_ON_MANAGER_START},
    {"UpdaterFetchAvailable", CLEAR_ON_MANAGER_START},
    {"UpdaterLastFetchTime", PERSISTENT},
    {"UpdaterNewDescription", CLEAR_ON_MANAGER_START},
    {"UpdaterNewReleaseNotes", CLEAR_ON_MANAGER_START},
    {"UpdaterState", CLEAR_ON_MANAGER_START},
    {"UpdaterTargetBranch", CLEAR_ON_MANAGER_START},
    {"Version", PERSISTENT},
    {"VisionRadarToggle", PERSISTENT},
    {"WheeledBody", PERSISTENT},
    {"carFingerprint", PERSISTENT},
    {"dp_0813", PERSISTENT},
    {"dp_alka", PERSISTENT},
    {"dp_cam_decel", PERSISTENT},
    {"dp_cam_decel_mode", PERSISTENT},
    {"dp_cam_decel_bump_dist", PERSISTENT},
    {"dp_cam_decel_bump_speed", PERSISTENT},
    {"dp_cam_decel_end", PERSISTENT},
    {"dp_cam_decel_safety_factor", PERSISTENT},
    {"dp_cam_decel_start", PERSISTENT},
    {"dp_car_assigned", PERSISTENT},
    {"dp_car_dashcam_mode_removal", PERSISTENT},
    {"dp_car_list", PERSISTENT},
    {"dp_device_audible_alert_mode", PERSISTENT},
    {"dp_device_auto_shutdown", PERSISTENT},
    {"dp_device_auto_shutdown_in", PERSISTENT},
    {"dp_device_disable_temp_check", PERSISTENT},
    {"dp_device_display_flight_panel", PERSISTENT},
    {"dp_device_display_off_mode", PERSISTENT},
    {"dp_device_enable_comma_registration", PERSISTENT},
    {"dp_device_no_ir_ctrl", PERSISTENT},
    {"dp_fileserv", PERSISTENT},
    {"dp_hkg_min_steer_speed_bypass", PERSISTENT},
    {"dp_lat_controller", PERSISTENT},
    {"dp_lat_lane_change_assist_speed", PERSISTENT},
    {"dp_lat_lane_priority_mode", PERSISTENT},
    {"dp_lat_lane_priority_mode_speed_based", PERSISTENT},
    {"dp_logging", PERSISTENT},
    {"dp_long_accel_btn", PERSISTENT},
    {"dp_long_accel_profile", PERSISTENT},
    {"dp_long_de2e", PERSISTENT},
    {"dp_long_missing_lead_warning", PERSISTENT},
    {"dp_long_personality_btn", PERSISTENT},
    {"dp_long_use_df_tune", PERSISTENT},
    {"dp_long_use_krkeegen_tune", PERSISTENT},
    {"dp_mapd", PERSISTENT},
    {"dp_mapd_vision_turn_control", PERSISTENT},
    {"dp_no_fan_ctrl", PERSISTENT},
    {"dp_no_gps_ctrl", PERSISTENT},
    {"dp_otisserv", PERSISTENT},
    {"dp_reset_conf", PERSISTENT},
    {"dp_toyota_auto_lock", PERSISTENT},
    {"dp_toyota_auto_unlock", PERSISTENT},
    {"dp_toyota_enhanced_bsm", PERSISTENT},
    {"dp_toyota_sng", PERSISTENT},
    {"dp_toyota_zss", PERSISTENT},
    {"dp_ui_rainbow", PERSISTENT},
    {"dp_vag_timebomb_bypass", PERSISTENT},
    {"error_description", PERSISTENT},
    {"uniqueID", PERSISTENT},

};

} // namespace


Params::Params(const std::string &path) {
  const char *prefix_env = getenv("OPENPILOT_PREFIX");
  std::string prefix;
  prefix += "/";
  prefix += (prefix_env ? prefix_env : "d");
  params_path = get_params_root(prefix, path);
}

std::vector<std::string> Params::allKeys() const {
  std::vector<std::string> ret;
  for (auto &p : keys) {
    ret.push_back(p.first);
  }
  return ret;
}

bool Params::checkKey(const std::string &key) {
  return keys.find(key) != keys.end();
}

ParamKeyType Params::getKeyType(const std::string &key) {
  return static_cast<ParamKeyType>(keys[key]);
}

int Params::put(const char* key, const char* value, size_t value_size) {
  std::string tmp_path = params_path + "/.tmp_value_XXXXXX";
  int tmp_fd = mkstemp((char*)tmp_path.c_str());
  if (tmp_fd < 0) return -1;

  int result = -1;
  do {
    ssize_t bytes_written = HANDLE_EINTR(write(tmp_fd, value, value_size));
    if (bytes_written < 0 || (size_t)bytes_written != value_size) {
      result = -20;
      break;
    }

    if ((result = fsync(tmp_fd)) < 0) break;

    FileLock file_lock(params_path + "/.lock");

    if ((result = rename(tmp_path.c_str(), getParamPath(key).c_str())) < 0) break;

    result = fsync_dir(getParamPath());
  } while (false);

  close(tmp_fd);
  ::unlink(tmp_path.c_str());
  return result;
}

int Params::remove(const std::string &key) {
  FileLock file_lock(params_path + "/.lock");
  int result = unlink(getParamPath(key).c_str());
  if (result != 0) {
    return result;
  }
  return fsync_dir(getParamPath());
}

std::string Params::get(const std::string &key, bool block) {
  if (!block) {
    return read_file(getParamPath(key));
  } else {
    params_do_exit = 0;
    void (*prev_handler_sigint)(int) = std::signal(SIGINT, params_sig_handler);
    void (*prev_handler_sigterm)(int) = std::signal(SIGTERM, params_sig_handler);

    std::string value;
    while (!params_do_exit) {
      if ((value = read_file(getParamPath(key))); !value.empty()) {
        break;
      }
      usleep(100000);  // 0.1 s
    }

    std::signal(SIGINT, prev_handler_sigint);
    std::signal(SIGTERM, prev_handler_sigterm);
    return value;
  }
}

std::map<std::string, std::string> Params::readAll() {
  FileLock file_lock(params_path + "/.lock");
  std::map<std::string, std::string> ret;
  if (DIR *d = opendir(getParamPath().c_str())) {
    struct dirent *de = NULL;
    while ((de = readdir(d))) {
      if (de->d_type != DT_DIR) {
        ret[de->d_name] = read_file(getParamPath(de->d_name));
      }
    }
    closedir(d);
  }
  return ret;
}

void Params::clearAll(ParamKeyType key_type) {
  FileLock file_lock(params_path + "/.lock");

  if (DIR *d = opendir(getParamPath().c_str())) {
    struct dirent *de = NULL;
    while ((de = readdir(d))) {
      if (de->d_type != DT_DIR) {
        auto it = keys.find(de->d_name);
        if (it == keys.end() || (it->second & key_type)) {
          unlink(getParamPath(de->d_name).c_str());
        }
      }
    }
    closedir(d);
  }

  fsync_dir(getParamPath());
}