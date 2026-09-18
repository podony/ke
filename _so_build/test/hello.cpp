#include <unordered_map>
#include <string>
std::unordered_map<std::string,int> m = {{"a",1}};
int main(){return m["a"];}