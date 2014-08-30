#include "TaskMonitor.hpp"
#include <iostream>
using namespace std;

int main()
{
    TaskMonitor tm;
    tm.readFlightOneway();
    tm.readFlightRound();
    tm.writeFlight();
    
    //tm.readRoom();
    //tm.writeRoom();
    
    /*
    string str = "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh";
    vector<string> vec;
    while(true)
    {
        vec.push_back(str);
        if( vec.size() % 10000 == 0)
            cout << vec.size() << endl;
    }
    */

    /*
    vector<string> vec;
    vec.push_back("1");
    vec.push_back("2");
    vec[0] = vec[1];
    vec[1] = "3";
    cout << vec[0] << "\t" << vec[1] << endl;
    */
    return 0;
}
