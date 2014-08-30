#ifndef _TASK_GENERATOR_HPP
#define _TASK_GENERATOR_HPP

/*
 *  AUTHOR: ZHANGYANG
 *  DATE: 2014.08.19
 *  BRIEF: TASK自动生成，根据task的监控信息，智能生成下一个5分钟的任务
 */

#include <string>
#include <vector>
#include <mysql/mysql.h>
#include "json/json.h"
#include "HotelGenerator.hpp"
#include "FlightGenerator.hpp"
using namespace std;

typedef tr1::unordered_map< string, tr1::unordered_map< string, tr1::unordered_map<string, string> > > DATA;
typedef tr1::unordered_map< string, tr1::unordered_map<string, string> > TYPE_DATA;
typedef tr1::unordered_map< string, float > TASK;

enum Type
{
    Flight=1, 
    Hotel=2
};

class TaskGenerator
{
    public:
        TaskGenerator();
        ~TaskGenerator();
        bool writeTask2DB(const string& host, const string& user, const string& passwd, const string& db);
        bool assignTaskByTimeslot(int timeslot);
        bool getTasks(const TYPE_DATA& type_data, TASK& tasks, Type type, int count);
        bool getLongtermTasks(const TYPE_DATA& type_data, TASK& tasks, Type type, int count);

    private:
        bool connect2DB(MYSQL* mysql, const string& host, const string& user, const string& passwd, const string& db);
        bool readData(Type type, const string& host, const string& db, const string& user, const string& passwd);
        bool isLongtermTask(const string& workload_key, Type type);
        bool isLongtermTimeslot(int timeslot);
        float getLongtermTaskScore(const string& workload_key, const string& updatetime);

    private:
        DATA m_regular_data;
        DATA m_longterm_data;
        TASK m_tasks;
        //TASK_SCORE m_flight_tasks;
        //TASK_SCORE m_longterm_hotel_tasks;
        //TASK_SCORE m_longterm_flight_tasks;
        DateTime m_today;
        DateTime m_now;
};


#endif  // _TASK_GENERATOR_HPP
