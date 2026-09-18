#pragma once
#include <string>
#include "common/util.h"
#include "system/hardware/base.h"
class HardwareEon : public HardwareNone {
public:
  static bool EON() { return true; }
  static std::string get_os_version() { return "NEOS"; }
};
