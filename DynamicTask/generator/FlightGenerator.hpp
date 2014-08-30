#ifndef _FLIGHT_GENERATOR_HPP
#define _FLIGHT_GENERATOR_HPP

/*
 *  AUTHOR: ZHANGYANG
 *  DATE: 2014.08.19
 *  BRIEF: 航班任务自动生成
 */

#include <string>
#include <vector>
#include <mysql/mysql.h>
#include "json/json.h"
using namespace std;

class FlightGenerator
{
    public:
        FlightGenerator();
        ~FlightGenerator();

    public:
        genNext5minTasks();

    private:
        bool connect2DB(const string& host, const string& user, const string& passwd, const string& db);
        bool getAirport();
        bool getCityScore();
        bool getAirportScore();
        bool getDayScore();
        bool getSourceScore();

};


#endif  // _FLIGHT_GENERATOR_HPP
