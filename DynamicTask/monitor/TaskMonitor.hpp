#ifndef _TASK_MONITOR_HPP
#define _TASK_MONITOR_HPP

/*
 * AUTHOR: ZHANGYANG
 * DATE:   2014.08.12
 * BRIEF:  TASK监控，通过每5分钟真实写入的数据，更新所有任务的完成情况
 *         flight: workload_key, 源, 上次更新时间, 价格, 本次更新时间, 本次价格, 变动
 *         room:   workload_key, 源, 上次更新时间, 价格, 本次更新时间, 本次价格, 变动
 */

#include <string>
#include <vector>
#include <tr1/unordered_map>
#include <mysql/mysql.h>
#include "json/json.h"
#include "key/KeyGenerator.hpp"
using namespace std;

typedef vector< vector<string> > CRAWL_DATA;
typedef tr1::unordered_map< string, vector<string> > MONITOR_DATA;

class TaskMonitor
{
    public:
        TaskMonitor();
        ~TaskMonitor();

        // 从crawl中读取flight表
        bool readFlightOneway();

        // 从crawl中读取flight_round表
        bool readFlightRound();
        
        /* 将航班监控信息写入数据库
         * 写入字段：workload_key, source, last_updatetime, last_price, update_time, price, price_wave
         */
        bool writeFlight();
        
        //
        bool readRoom();
        
        //
        bool writeRoom();
        
        //
        bool monitor();
    private:
        bool connect2DB(MYSQL* m_mysql, const string& host, const string& db, const string& user, const string& passwd);
        bool createMonitorTable(const string& host, const string& db, const string& user, const string& passwd);
        void insertFlightMonitorData(const MONITOR_DATA& monitor_data, MONITOR_DATA& diff_monitor_data, const string& workload, const string& source, const string& updatetime, const string& price_str, const string& dept_id, const string& dest_id);
        void insertHotelMonitorData(const MONITOR_DATA& monitor_data, MONITOR_DATA& diff_monitor_data, const string& workload, const string& source, const string& updatetime, const string& price_str);
        bool readMonitorData(MONITOR_DATA& monitor_data, const string& sql, int num_fields, const string& host, const string& db, const string& user, const string& passwd);
        bool updateFlightMonitorData(const MONITOR_DATA& diff_monitor_data, const string& host, const string& db, const string& user, const string& passwd);
        bool updateRoomMonitorData(const MONITOR_DATA& diff_monitor_data, const string& host, const string& db, const string& user, const string& passwd);
        string serializePrice(const Json::Value& price_value);
        bool parsePrice(const string& price_str, Json::Value& price_value);
        float getPriceWave(const string& last_price_str, const string& price_str);
        
        inline void stripDay(string& day)
        {
            string year = day.substr(0, 4);
            string month = day.substr(5, 2);
            string date = day.substr(8, 2);
            day = year + month + date;
        }
    private:
        CRAWL_DATA m_flight_crawl_data;
        CRAWL_DATA m_room_crawl_data;
        MONITOR_DATA m_flight_monitor_data;
        MONITOR_DATA m_room_monitor_data;
        KeyGenerator* m_key_generator;
};





#endif  // TASK_MONITOR_HPP
