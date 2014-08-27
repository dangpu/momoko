#include "validation.hpp"

int main()
{
    Validation val;
    string req = "MU8667|PEK|CDG|20140911_09:05|经济舱|ctrip";
    string res = "";
    val.registerSlave("42.96.192.130:8818", true);
    val.handleValidReq(req, "flight", res);
    
    cout << "res is:" << res << endl;
    return 0;
}
