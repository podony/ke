#include <cstring>
#include <cstdint>
static uint32_t f(const uint8_t* p){ uint32_t r; std::memcpy(&r,p,4); return r; }
extern "C" uint32_t callf(const uint8_t* p){ return f(p); }
