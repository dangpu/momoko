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
#include "KeyGenerator"
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
        void insertMonitorData(const string& workload, const string& source, const string& updatetime, const string& price_str);
        bool readMonitorData(MONITOR_DATA& monitor_data, const string& sql, const string& host, const string& db, const string& user, const string& passwd);
        string serializePrice(const Json::Value& price_value);
        bool parsePrice(const string& price_str, Json::Value& price_value);
        float getPriceWave(const string& last_price_str, const string& price_str);
    private:
        CRAWL_DATA m_crawl_data;
        MONITOR_DATA m_monitor_data;
        KeyGenerator* m_key_generator;
};





#endif  // TASK_MONITOR_HPP
