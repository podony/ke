
#include <unordered_map>
#include <string>
#include <cstdint>
int main(){ std::unordered_map<std::string,uint32_t> m; m["x"]=2; return (int)m["x"]; }

