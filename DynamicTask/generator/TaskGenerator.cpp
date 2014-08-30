#include <iostream>
#include "TaskGenerator.hpp"
using namespace std;


#define FLIGHT_NUM   5000
#define HOTEL_NUM   5000


TaskGenerator::TaskGenerator()
{
}


TaskGenerator::~TaskGenerator()
{
}


bool TaskGenerator::writeTask2DB(const string& host, const string& user, const string& passwd, const string& db)
{
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {   
        return false;
    }
    string sql;
    
    // 写长期任务
    

    // 写短期任务
}

bool TaskGenerator::assignTaskByTimeslot(int timeslot)
{
    if( isLongtermTimeslot(timeslot) ) 
    {
        // 分配长期任务
        getLongtermTasks(m_longterm_data[Type.Flight], m_tasks, Type.Flight, FLIGHT_NUM);
        getLongtermTasks(m_longterm_data[Type.Hotel], m_tasks, Type.Hotel, HOTEL_NUM);
    }
    else
    {
        // 分配例行任务
        getTasks(m_regular_data[Type.Flight], m_tasks, Type.Flight, FLIGHT_NUM);
        getTasks(m_regular_data[Type.Hotel], m_tasks, Type.Hotel, HOTEL_NUM);
    }
    return true;
}


bool TaskGenerator::getTasks(const TYPE_DATA& type_data, TASK& tasks, Type type, int count)
{
    // 判断task类型
    if(type == Type.Flight)
    {
        m_generator = new FlightGenerator();
    }
    else if(type == Type.Hotel)
    {
        m_generator = new HotelGenerator();
    }
    else
    {
        _ERROR("[In TaskGenerator::getRegularTasks, unknown type!]");
    }

    // 获取所有task的得分
    for(TYPE_DATA::iterator it = type_data.begin(); it != type_data.end(); ++it)
    {
        string workload_key = it->first;
        string updatetime = (it->second)["updatetime"];
        float price_wave = atof( (it->second)["price_wave"].c_str() );
        float score = m_generator->getTaskScore(workload_key, updatetime, price_wave);
        // 插入该task的得分
        tasks[workload_key] = score;
    }
    
    // 排序
    ；

    return true;
}


bool TaskGenerator::getLongtermTasks(const TYPE_DATA& type_data, TASK& tasks, Type type, int count)
{
    // 首先执行长期任务共有逻辑
    getLongtermTaskScore(type_data, tasks);

    // 然后根据各类型分别计算得分
    getTasks(type_data, tasks, type, count);
}


bool TaskGenerator::connect2DB(MYSQL* mysql, const string& host, const string& user, const string& passwd, const string& db)
{
    mysql_init(mysql);
    if (!mysql_real_connect(mysql, host.c_str(), user.c_str(), passwd.c_str(), db.c_str(), 0, NULL, 0))
    {
        _ERROR("[Connect to %s error: %s]", db.c_str(), mysql_error(mysql));
        return false;
    }
    // 设置字符编码
    if (mysql_set_character_set(mysql, "utf8"))
    {
        _ERROR("[Set mysql characterset: %s]", mysql_error(mysql));
        return false;
    }
    return true;
}


bool TaskGenerator::readData(Type type, const string& host, const string& db, const string& user, const string& passwd)
{
    string sql;
    if(type == Type.Flight)
    {
        sql = "SELECT workload_key, source, updatetime, price_wave FROM flight_monitor";
    }
    if(type == Type.Hotel)
    {
        sql = "SELECT workload_key, source, updatetime, price_wave FROM room_monitor";
    }

    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {   
        return false;
    }   
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {   
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
        return false;
    }   
    else
    {   
        MYSQL_RES* res = mysql_use_result(mysql);
        MYSQL_ROW row;
        if(res)
        {   
            while( row = mysql_fetch_row(res) )
            {
                tr1::unordered_map<string, string> task_map;
                string workload_key = row[0];
                string source = row[1];
                string updatetime = row[2];
                string price_wave = row[3];
                task_map["key"] = workload_key;
                task_map["source"] = source;
                task_map["updatetime"] = updatetime;
                task_map["wave"] = price_wave;
                // 判断是否为长期任务
                if( isLongtermTask(workload_key, type) )
                {
                    m_longterm_data[type][workload_key] = task_map;
                }
                else
                {
                    m_regular_data[type][workload_key] = task_map;
                }
            }   
        }   
        mysql_free_result(res);
    }
    mysql_close(mysql);
    delete mysql;
    return true;
}


bool TaskGenerator::isLongtermTask(const string& workload_key, Type type)
{
    // 获得crawl_day
    string crawl_day = ""
    vector<string> vec;
    if( Type.Flight == type )
    {
        SplitString(workload_key, &vec, "|");
        if( vec.size() < 4 )
        {
            _ERROR("[ In isLongtermTask, Wrong workload_key! ]");
        }
        crawl_day = vec[3];
    }
    else if( Type.Hotel == type )
    {
        SplitString(workload_key, &vec, "_");
        if( vec.size() != 5 )
        {
            _ERROR("[ In isLongtermTask, Wrong workload_key! ]");
        }
        crawl_day = vec[4]
    }
    // 判断是否长期
    DateTime crawl_dt = DateTime::Parse(crawl_day, "yyyyMMdd");
    TimeSpan ts = crawl_dt - m_today;
    int interval_days = ts.GetDays();
    if( 5 < interval_days < 10 || 31 < interval_days < 70)
    {
        return true;
    }
    else
    {
        return false;
    }
}


bool TaskGenerator::isLongtermTimeslot(int timeslot)
{
    if( timeslot < 72 && timeslot > 0)
        return true;
    else
        return false;
}


float TaskGenerator::getLongtermTaskScore(const string& workload_key, const string& updatetime)
{
    // 获取未更新时间（秒）
    Datetime update_dt  = DateTime::Parse(updatetime, "");
    TimeSpan ts = m_now - update_dt;
    int non_update_seconds = ts.GetSeconds();
    // 5天还未更新，赋予极高的得分
    if(non_update_seconds > 5*86400)
        return 100.0;
    else
        return 0.0;
}
