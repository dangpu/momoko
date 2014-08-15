#ifndef _KEY_GENERATOR_HPP
#define _KEY_GENERATOR_HPP

/*
 * AUTHOR: ZHANGYANG
 * DATE: 2014.08.13
 * BRIEF: workload_key生成器，包括flight oneway， flight round， room
 */

#include <string>
#include <vector>
#include <tr1/unordered_map>
#include <mysql/mysql.h>
using namespace std;

typedef tr1::unordered_map< tr1::unordered_map<string> > FLIGHT_DATA;
typedef tr1::unordered_map< vector< pair<string, string> > > FLIGHT_PAIR;

class KeyGenerator
{
    public:
        KeyGenerator();
        ~KeyGenerator();

        string getFlightOnewayKey(const string& source, const string& dept_id, const string& dest_id, const string& dept_day);
        string getFlightRoundKey(const string& source, const string& dept_id, const string& dest_id, const string& dept_day, const string& dest_day);
        string getRoomKey(const string& source, const string& city_name, const string& hotel_id, const string& checkin_day, int days);

    private:
        bool connect2DB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd);
        
        // 载入机场数据，m_airport
        bool loadAirport();
        
        // 载入航班源数据，m_flight_source
        bool loadFlightSource();

        // 载入航班航线信息，m_flight_pair
        bool loadFlightPair();
        
        /* 解析航班rule
         * @param: dept_id, 出发机场
         * @param: dest_id, 到达机场
         * @return: workload_key
         */
        string getKeyFromRule(const string& dept_id, const string& dest_id);
    private:
        FLIGHT_DATA m_airport;              // 机场数据
        FLIGHT_DATA m_flight_source;        // 航班源信息
        FLIGHT_PAIR m_flight_pair;          // 航班航线信息
};

#endif //  _KEY_GENERATOR_HPP
