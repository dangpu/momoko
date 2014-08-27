#ifndef _STRING_TOOLS_H_
#define _STRING_TOOLS_H_


#include <string>
#include <vector>

class StrTools
{
    public:
        StrTools(){};
        ~StrTools(){};
    public:
        int split(const std::string& str, const std::string& pattern, std::vector<std::string>& v);
        std::string substr(const std::string& s, const std::string& begin_pattern, const std::string& end_pattern);
        std::string toLowerCase(const std::string& s);
        std::string toUpperCase(const std::string& s);
};

#endif
