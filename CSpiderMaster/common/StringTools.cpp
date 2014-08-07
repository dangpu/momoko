#include "StringTools.h"
using namespace std;
// 分割字符串
int StrTools::split(const string& str, const string& pattern, vector<string>& v)
{
    v.clear();
    size_t bpos = 0;

    while(str.find(pattern, bpos) != std::string::npos)
    {
        size_t epos = str.find(pattern, bpos);
        if(epos == 0)
        {
            bpos = epos + pattern.size();
            continue;
        }
        v.push_back(str.substr(bpos, epos - bpos));
        bpos = epos + pattern.size();
        if(bpos >= str.size())
            break;
    }

    if(bpos < str.size())
        v.push_back(str.substr(bpos, str.size() - bpos));

    return v.size();
}

// 取特定子串
string StrTools::substr(const string& s, const string& begin_pattern, const string& end_pattern)
{
    string retstr = "";
    size_t bpos = s.find(begin_pattern);
    size_t epos = 0;

    if(bpos != string::npos)
    {   
        bpos += begin_pattern.size();
        if(bpos >= s.size())
            return retstr;

        epos = s.find(end_pattern, bpos);
        if(epos != string::npos)
            retstr = s.substr(bpos, epos - bpos);
        else
            retstr = s.substr(bpos, s.size() - bpos);
    }
    return retstr;
}

string StrTools::toLowerCase(const string& s)
{
    string ret = s;
    for(int i = 0; i < ret.size(); ++i)
    {
        if((int)ret[i] >= 65 and (int)ret[i] <= 90)
            ret[i] += 32;
    }
    return ret;
}

string StrTools::toUpperCase(const string& s)
{
    string ret = s;
    for(int i = 0; i < ret.size(); ++i)
    {
        if((int)ret[i] >= 97 and (int)ret[i] <= 122)
            ret[i] -= 32;
    }
    return ret;
}

