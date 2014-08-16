#include "TaskMonitor.hpp"

int main()
{
    TaskMonitor tm;
    //tm.readFlightOneway();
    //tm.readFlightRound();
    //tm.writeFlight();
    
    tm.readRoom();
    tm.writeRoom();
    return 0;
}
