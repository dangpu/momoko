#include <sstream>
#include <fstream>
#include <iostream>
#include <math.h>
#include "common/service_log.hpp"
#include "CommonFuc.hpp"
#include "TaskMonitor.hpp"

// 单程航班crawl字段数
#define FLIGHT_ONEWAY_NUM_FIELDS    7
// 往返航班crawl字段数
#define FLIGHT_ROUND_NUM_FIELDS     9
// 酒店crawl字段数
#define ROOM_NUM_FIELDS             8
// 监控表字段数
#define ROOM_MONITOR_NUM_FIELDS   7
#define FLIGHT_MONITOR_NUM_FIELDS   9


TaskMonitor::TaskMonitor()
{
    if( !createMonitorTable("127.0.0.1", "monitor", "root", "wangjingsoho") )
    {
        _ERROR("In TaskMonitor, cannot create monitor table!");
    }
    m_key_generator = new KeyGenerator();
}


TaskMonitor::~TaskMonitor()
{
    delete m_key_generator;
}


bool TaskMonitor::connect2DB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd)
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

bool TaskMonitor::createMonitorTable(const string& host, const string& db, const string& user, const string& passwd)
{
    // 连接数据库
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {   
        return false;
    }
    // 建flight_monitor
    ostringstream oss;
    oss << "create table if not exists flight_monitor (id int unsigned not null auto_increment primary key, workload_key varchar(128) NOT NULL UNIQUE, source varchar(24), dept_id varchar(8), dest_id varchar(8), last_updatetime varchar(64), "
        << "last_price varchar(128), updatetime varchar(64), price varchar(128), price_wave varchar(24)) default charset=utf8;";
    string create_flight_monitor_sql = oss.str();
    int t = mysql_query(mysql, create_flight_monitor_sql.c_str());
    if(t != 0)                                                                                                                                                                                                                            
    {                                                                                                                                                                                                                                     
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), create_flight_monitor_sql.c_str());
        mysql_close(mysql);                                                                                                                                                                                                             
        return false;                                                                                                                                                                                                                     
    }
    // 建立room_monitor表
    ostringstream oss1;
    oss1 << "create table if not exists room_monitor (id int unsigned not null auto_increment primary key, workload_key varchar(128) NOT NULL UNIQUE, source varchar(24), last_updatetime varchar(64), last_price varchar(128), "
         << "updatetime varchar(64), price varchar(128), price_wave varchar(24)) default charset=utf8;";
    string create_room_monitor_sql = oss1.str();
    t = mysql_query(mysql, create_room_monitor_sql.c_str());
    if(t != 0)                                                                                                                                                                                                                            
    {                                                                                                                                           
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), create_room_monitor_sql.c_str());                                                                                                                                             
        mysql_close(mysql);                                                                                                                                                                                                             
        return false;                                                                                                                                                                                                                     
    }                                                                                                                                                                                                                                     
    mysql_close(mysql);                                                                                                                                                                                                                 
    delete mysql;
    return true;
}

bool TaskMonitor::readFlightOneway()
{
    // 连接数据库
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    string host = "114.215.168.168";
    string db = "crawl";
    string user = "root";
    string passwd = "miaoji@2014!";
    if( !connect2DB(mysql, host, db, user, passwd) )
    {   
        return false;
    }
    
    // 读取flight表
    // 航班号，出发城市三字码，到达城市三字码，出发日期，价格，更新时间, 源
    string sql = "select flight_no, dept_id, dest_id, dept_day, price, updatetime, source from flight ORDER BY dept_id, dest_id, dept_day, source";
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {   
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
    }   
    else
    {   
        MYSQL_RES* res = mysql_use_result(mysql);
        int num_fields = mysql_num_fields(res);
        if(num_fields != FLIGHT_ONEWAY_NUM_FIELDS)
        {
            _ERROR("READ flight, wrong num fields : %d!", num_fields);
            return false;
        }
        MYSQL_ROW row;
        if(res)
        {
            string last_dept_id;
            string last_dest_id;
            string last_dept_day;
            string last_source;
            string last_updatetime;
            Json::Value price_value;
            while( row = mysql_fetch_row(res) )
            {
                string flight_no = row[0];
                string dept_id = row[1];
                string dest_id = row[2];
                string dept_day = row[3];
                stripDay(dept_day);
                string price = row[4];
                string updatetime = row[5];
                string raw_source = row[6];                                             // expidia::expidia
                string source = raw_source.substr( 0, raw_source.find("::") );         // 解析出expidia
                // 判断该记录和上条记录是否属于同一个task
                if( dept_id == last_dept_id && dest_id == last_dest_id && dept_day == last_dept_day && source == last_source)
                {
                    price_value["flight_num"] = price_value.get("flight_num", 0).asInt() + 1;
                    price_value["price_all"] = price_value.get("price_all", 0.0).asDouble() + atof(price.c_str());
                    //price_value[flight_no] = atof(price.c_str());
                }
                else
                {
                    // 价格序列化
                    string price_str = serializePrice(price_value);
                    // 读入该条任务执行情况
                    vector<string> vec;
                    vec.push_back(last_dept_id);
                    vec.push_back(last_dest_id);
                    vec.push_back(last_dept_day);
                    vec.push_back(price_str);
                    vec.push_back(last_updatetime);
                    vec.push_back(last_source);
                    if(last_source != "")
                        m_flight_crawl_data.push_back(vec);
                    // 清空价格
                    price_value.clear();
                    // 记录新任务
                    //price_value[flight_no] = atof(price.c_str());
                    price_value["flight_num"] = 1;
                    price_value["price_all"] = atof(price.c_str());
                }
                // 更新任务指示器
                last_dept_id = dept_id;
                last_dest_id = dest_id;
                last_dept_day = dept_day;
                last_source = source;
                last_updatetime = updatetime;
            }
            // 最后一个workload 更新
            // TODO
        }
        mysql_free_result(res);
    }
    _INFO("read flight oneway ok!");
    // 删除mysql
    mysql_close(mysql);
    delete mysql;
    return true;
}


bool TaskMonitor::readFlightRound()
{
    // 连接数据库
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    string host = "114.215.168.168";
    string db = "crawl";
    string user = "root";
    string passwd = "miaoji@2014!";
    if( !connect2DB(mysql, host, db, user, passwd) )
    {   
        return false;
    }
    
    // 读取flight_round表
    // 出发航班号，出发城市三字码，归来航班号，到达城市三字码，出发日期，归来日期， 价格，更新时间, 源
    string sql = "select flight_no_A, dept_id, flight_no_B, dest_id, dept_day, dest_day, price, updatetime, source from flight_round ORDER BY dept_id, dest_id, dept_day, dest_day, source";
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {   
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
        return false;
    }   
    else
    {   
        MYSQL_RES* res = mysql_use_result(mysql);
        int num_fields = mysql_num_fields(res);
        if(num_fields != FLIGHT_ROUND_NUM_FIELDS)
        {
            _ERROR("READ flight_round, wrong num fields: %d!", num_fields);
            return false;
        }
        MYSQL_ROW row;
        if(res)
        {
            string last_dept_id;
            string last_dest_id;
            string last_dept_day;
            string last_dest_day;
            string last_source;
            string last_updatetime;
            Json::Value price_value;
            while( row = mysql_fetch_row(res) )
            {
                string flight_no_A = row[0];
                string dept_id = row[1];
                string flight_no_B = row[2];
                string dest_id = row[3];
                string dept_day = row[4];
                stripDay(dept_day);
                string dest_day = row[5];
                stripDay(dest_day);
                string price = row[6];
                string updatetime = row[7];
                string raw_source = row[8];
                string source = raw_source.substr( 0, raw_source.find("::") ) + "Round";         // 解析出jijitongRound
                // 判断该记录和上条记录是否属于同一个task
                if( dept_id == last_dept_id && dest_id == last_dest_id && dept_day == last_dept_day && dest_day == last_dest_day && source == last_source)
                {
                    price_value["flight_num"] = price_value.get("flight_num", 0).asInt() + 1;
                    price_value["price_all"] = price_value.get("price_all", 0.0).asDouble() + atof(price.c_str());
                    //string flight_no = flight_no_A + '&' + flight_no_B;
                    //price_value[flight_no] = atof(price.c_str());
                }
                else
                {
                    // 价格序列化
                    string price_str = serializePrice(price_value);
                    // 读入该条任务执行情况
                    vector<string> vec;
                    vec.push_back(last_dept_id);
                    vec.push_back(last_dest_id);
                    vec.push_back(last_dept_day);
                    vec.push_back(last_dest_day);
                    vec.push_back(price_str);
                    vec.push_back(last_updatetime);
                    vec.push_back(last_source);
                    if(last_source != "")
                        m_flight_crawl_data.push_back(vec);
                    // 清空价格
                    price_value.clear();
                    // 记录新任务
                    price_value["flight_num"] = 1;
                    price_value["price_all"] = atof(price.c_str());
                    //string flight_no = flight_no_A + '&' + flight_no_B;
                    //price_value[flight_no] = atof(price.c_str());
                }
                // 更新任务指示器
                last_dept_id = dept_id;
                last_dest_id = dest_id;
                last_dept_day = dept_day;
                last_dest_day = dest_day;
                last_source = source;
                last_updatetime = updatetime;
            }
            // 最后一个workload 更新
            // TODO
        }
        mysql_free_result(res);
    }
    // 删除mysql
    mysql_close(mysql);
    delete mysql;
    return true;
}


bool TaskMonitor::writeFlight()
{
    // 读取现有监控数据
    string host = "121.199.43.226";
    string db = "monitor";
    string user = "root";
    string passwd = "wangjingsoho";
    string sql = "select workload_key, source, last_updatetime, last_price, updatetime, price, price_wave, dept_id, dest_id from flight_monitor";
    if( !readMonitorData(m_flight_monitor_data, sql, FLIGHT_MONITOR_NUM_FIELDS, host, db, user, passwd) )
    {
        _ERROR("IN writeFlight, CANNOT read monitor data!");
        return false;
    }

    // 更新现有监控数据
    MONITOR_DATA diff_monitor_data;
    CRAWL_DATA::iterator it = m_flight_crawl_data.begin();
    for(; it != m_flight_crawl_data.end(); ++it)
    {
        vector<string> crawl_vec = *it;
        string workload_key;
        if( FLIGHT_ONEWAY_NUM_FIELDS-1 == crawl_vec.size() )
        {   
            // 单程航班
            string source = crawl_vec[5];
            string dept_id = crawl_vec[0];
            string dest_id = crawl_vec[1];
            string dept_day = crawl_vec[2];
            string price_str = crawl_vec[3];
            string updatetime = crawl_vec[4];
            // 生成workload_key
            //_INFO("[%s, %s, %s, %s]", source.c_str(), dept_id.c_str(), dest_id.c_str(), dept_day.c_str());
            workload_key = m_key_generator->getFlightOnewayKey(source, dept_id, dest_id, dept_day);
            cout << workload_key << " " << dept_id << " " << dest_id << endl;
            // 插入
            insertFlightMonitorData(m_flight_monitor_data, diff_monitor_data, workload_key, source, updatetime, price_str, dept_id, dest_id);
        }
        else if( FLIGHT_ROUND_NUM_FIELDS-2 == crawl_vec.size() )
        {
            // 往返航班
            string dept_id = crawl_vec[0];
            string dest_id = crawl_vec[1];
            string dept_day = crawl_vec[2];
            string dest_day = crawl_vec[3];
            string price_str = crawl_vec[4];
            string updatetime = crawl_vec[5];
            string source = crawl_vec[6];
            // 生成workload_key
            workload_key = m_key_generator->getFlightRoundKey(source, dept_id, dest_id, dept_day, dest_day);
            // 插入
            insertFlightMonitorData(m_flight_monitor_data, diff_monitor_data, workload_key, source, updatetime, price_str, dept_id, dest_id);
        }
        else
        {
            _ERROR("");
            continue;
        }
        //cout << workload_key << "\t" << m_flight_monitor_data[workload_key][1] << "\t" << m_flight_monitor_data[workload_key][2] << "\t" << m_flight_monitor_data[workload_key][3] << "\t" << m_flight_monitor_data[workload_key][4] << "\t" << m_flight_monitor_data[workload_key][5] << "\t" << m_flight_monitor_data[workload_key][6] << "\t" << m_flight_monitor_data[workload_key][7] << "\t" << m_flight_monitor_data[workload_key][8] << endl;
    }
    
    // 监控数据写回数据库
    updateFlightMonitorData(diff_monitor_data, host, db, user, passwd);
        

    return true;
}


bool TaskMonitor::readRoom()
{
    // 连接crawl数据库
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    string host = "114.215.168.168";
    string db = "crawl";
    string user = "root";
    string passwd = "miaoji@2014!";
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }

    // 读取room表
    // 城市, 源, 源酒店id, 源房间id, 入住日期, 离店日期, 价格, 更新时间
    string sql = "SELECT city, source, source_hotelid, source_roomid, check_in, check_out, price, update_time FROM room ORDER BY city, check_in, check_out, source, source_hotelid";
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {   
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
    }
    else
    {
        MYSQL_RES* res = mysql_use_result(mysql);
        int num_fields = mysql_num_fields(res);
        if(num_fields != ROOM_NUM_FIELDS)
        {
            _ERROR("READ room, wrong num fields : %d!", num_fields);
            return false;
        }
        MYSQL_ROW row;
        if(res)
        {
            string last_source;
            string last_city;
            string last_source_hotelid;
            string last_checkin_day;
            string last_checkout_day;
            string last_updatetime;
            Json::Value price_value;
            while( row = mysql_fetch_row(res) )
            {
                string city = row[0];
                string source = row[1];
                string source_hotelid = row[2];
                string source_roomid = row[3];
                string checkin_day = row[4];
                string checkout_day = row[5];
                if(checkin_day == "NULL" || checkout_day == "NULL")
                    continue;
                stripDay(checkin_day);
                stripDay(checkout_day);
                string price = row[6];
                string updatetime = row[7];
                bool flag = false;      // 标示该条记录和上一条记录是否属于同一个workload
                // 对于按城市抓取的源和按酒店抓取的源分别判断该条记录和上一条记录是否属于同一个workload
                if(source == "biyi" || source == "agoda")
                {
                    if(city == last_city && source == last_source && checkin_day == last_checkin_day && checkout_day == last_checkout_day)
                    {
                        flag = true;
                    }
                }
                else
                {
                    if(source_hotelid == last_source_hotelid && source == last_source && checkin_day == last_checkin_day && checkout_day == last_checkout_day)
                    {
                        flag = true;
                    }
                }
                //
                if(flag)
                {
                    if(source_roomid == "NULL")
                    {
                        price_value["room_num"] = price_value.get("room_num", 0).asInt() + 1;
                        price_value["price_all"] = price_value.get("price_all", 0.0).asDouble() + atof(price.c_str());
                    }
                    else
                    {
                        price_value["room_num"] = price_value.get("room_num", 0).asInt() + 1;
                        price_value["price_all"] = price_value.get("price_all", 0.0).asDouble() + atof(price.c_str());
                        //price_value[source_roomid] = atof(price.c_str());
                    }
                }
                else
                {
                    // 价格序列化
                    string price_str = serializePrice(price_value);
                    price_value.clear();
                    // 读入该条任务执行情况
                    vector<string> vec;
                    vec.push_back(last_city);
                    vec.push_back(last_source);
                    vec.push_back(last_source_hotelid);
                    vec.push_back(last_checkin_day);
                    vec.push_back(last_checkout_day);
                    vec.push_back(price_str);
                    vec.push_back(last_updatetime);
                    // 插入到crawl数据
                    if(last_city != "")
                        m_room_crawl_data.push_back(vec);
                    // 记录新任务
                    if(source_roomid == "NULL")
                    {
                        price_value["room_num"] = price_value.get("room_num", 0).asInt() + 1;
                        price_value["price_all"] = price_value.get("price_all", 0.0).asDouble() + atof(price.c_str());
                    }
                    else
                    {
                        price_value["room_num"] = price_value.get("room_num", 0).asInt() + 1;
                        price_value["price_all"] = price_value.get("price_all", 0.0).asDouble() + atof(price.c_str());
                        //price_value[source_roomid] = atof(price.c_str());
                    }
                    
                }
                // 更新为上一条记录
                last_city = city;
                last_source = source;
                last_source_hotelid = source_hotelid;
                last_checkin_day = checkin_day;
                last_checkout_day = checkout_day;
                last_updatetime = updatetime;
            }
        }
        mysql_free_result(res);
    }
    mysql_close(mysql);
    delete mysql;
    return true;
}


bool TaskMonitor::writeRoom()
{
    // 读取现有monitor数据
    string host = "121.199.43.226";
    string db = "monitor";
    string user = "root";
    string passwd = "wangjingsoho";
    string sql = "select workload_key, source, last_updatetime, last_price, updatetime, price, price_wave from room_monitor";
    if( !readMonitorData(m_room_monitor_data, sql, ROOM_MONITOR_NUM_FIELDS, host, db, user, passwd) )
    {
        _ERROR("IN writeFlight, CANNOT read monitor data!");
        return false;
    }

    // 插入crawl数据
    MONITOR_DATA diff_monitor_data;
    CRAWL_DATA::iterator it = m_room_crawl_data.begin();
    for(; it != m_room_crawl_data.end(); ++it)
    {
        vector<string> crawl_vec = *it;
        string workload_key;
        if( ROOM_NUM_FIELDS-1 == crawl_vec.size() )
        {
            string city = crawl_vec[0];
            string source = crawl_vec[1];
            string source_hotelid = crawl_vec[2];
            string checkin_day = crawl_vec[3];
            string checkout_day = crawl_vec[4];
            string price_str = crawl_vec[5];
            string updatetime = crawl_vec[6];
            // 生成workload_key
            workload_key = m_key_generator->getRoomKey(source, city, source_hotelid, checkin_day, checkout_day);
            // 插入
            insertHotelMonitorData(m_room_monitor_data, diff_monitor_data, workload_key, source, updatetime, price_str);
        }
        else
        {
            _ERROR("");
            continue;
        }
        //cout << workload_key << "\t" << m_room_monitor_data[workload_key][2] << "\t" << m_room_monitor_data[workload_key][3] << "\t" << m_room_monitor_data[workload_key][4] << "\t" << m_room_monitor_data[workload_key][5] << "\t" << m_room_monitor_data[workload_key][6] << "\t" << m_room_monitor_data[workload_key][7] << endl;
    }
    
    updateRoomMonitorData(diff_monitor_data, host, db, user, passwd);

    return true;
}


void TaskMonitor::insertHotelMonitorData(const MONITOR_DATA& monitor_data, MONITOR_DATA& diff_monitor_data, const string& workload_key, const string& source, const string& updatetime, const string& price_str)
{
    // 插入
    MONITOR_DATA::const_iterator it = monitor_data.find(workload_key);
    if( it != monitor_data.end() )
    {
        // 存在该key， 更新
        vector<string> monitor_vec = it->second;
        cout << "ZHANGYANG " << workload_key << "\t" << monitor_vec[2] << "\t" << updatetime << endl;
        monitor_vec[2] = monitor_vec[4];                                // 更新last_updatetime
        monitor_vec[3] = monitor_vec[5];                                // 更新last_price
        monitor_vec[4] = updatetime;                                    // 更新updatetime
        monitor_vec[5] = price_str;                                     // 更新price
        ostringstream oss;
        oss << getPriceWave(monitor_vec[3], monitor_vec[5]);
        monitor_vec[6] = oss.str();                                     // 更新price变动
        diff_monitor_data[workload_key] = monitor_vec;                     // 更新monitor_data
    }
    else
    {
       // 不存在该key， 插入
       vector<string> monitor_vec;
       monitor_vec.push_back(workload_key);
       monitor_vec.push_back(source);
       monitor_vec.push_back("NULL");
       monitor_vec.push_back("NULL");
       monitor_vec.push_back(updatetime);
       monitor_vec.push_back(price_str);
       ostringstream oss;
       oss << getPriceWave("NULL", price_str);
       monitor_vec.push_back( oss.str() );
       //monitor_vec.push_back(str1);
       //monitor_vec.push_back(str2);
       diff_monitor_data[workload_key] = monitor_vec;
    }
}

void TaskMonitor::insertFlightMonitorData(const MONITOR_DATA& monitor_data, MONITOR_DATA& diff_monitor_data, const string& workload_key, const string& source, const string& updatetime, const string& price_str, const string& dept_id, const string& dest_id)
{
    // 插入
    MONITOR_DATA::const_iterator it = monitor_data.find(workload_key);
    if( it != monitor_data.end() )
    {
        // 存在该key， 更新
        vector<string> monitor_vec = it->second;
        cout << "ZHANGYANG " << workload_key << "\t" << monitor_vec[2] << "\t" << updatetime << endl;
        monitor_vec[2] = monitor_vec[4];                                // 更新last_updatetime
        monitor_vec[3] = monitor_vec[5];                                // 更新last_price
        monitor_vec[4] = updatetime;                                    // 更新updatetime
        monitor_vec[5] = price_str;                                     // 更新price
        ostringstream oss;
        oss << getPriceWave(monitor_vec[3], monitor_vec[5]);
        monitor_vec[6] = oss.str();                                     // 更新price变动
        diff_monitor_data[workload_key] = monitor_vec;                     // 更新monitor_data
    }
    else
    {
       // 不存在该key， 插入
       vector<string> monitor_vec;
       monitor_vec.push_back(workload_key);
       monitor_vec.push_back(source);
       monitor_vec.push_back("NULL");
       monitor_vec.push_back("NULL");
       monitor_vec.push_back(updatetime);
       monitor_vec.push_back(price_str);
       ostringstream oss;
       oss << getPriceWave("NULL", price_str);
       monitor_vec.push_back( oss.str() );
       monitor_vec.push_back(dept_id);
       monitor_vec.push_back(dest_id);
       diff_monitor_data[workload_key] = monitor_vec;
    }
}

bool TaskMonitor::readMonitorData(MONITOR_DATA& monitor_data, const string& sql, int num_fields, const string& host, const string& db, const string& user, const string& passwd)   
{
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
        if(num_fields != mysql_num_fields(res))
        {
            _ERROR("IN readMonitorData, num_fields not match, real num_fields is %d", mysql_num_fields(res));
            return false;
        }
        MYSQL_ROW row;
        if(res)
        {
            while( row = mysql_fetch_row(res) )
            {
                vector<string> vec;
                for(int i = 0; i < num_fields; i++)
                {
                    vec.push_back(string(row[i]));
                }
                monitor_data[row[0]] = vec;
            } 
        }
        mysql_free_result(res);
    }

    int num = 0;
    map<string, int> test_map;
    for(MONITOR_DATA::iterator it = monitor_data.begin(); it != monitor_data.end(); ++it)
    {
        string key = it->first;
        test_map[key] = 1;
        num++;
    }
    cout << "zhangyang, in monitor data, workload num and monitor rows are: " << test_map.size()  << "\t" << num << endl;

    mysql_close(mysql);
    delete mysql;
    return true;
}

bool TaskMonitor::updateFlightMonitorData(const MONITOR_DATA& diff_monitor_data, const string& host, const string& db, const string& user, const string& passwd)  
{
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }
    // 生成更新sql
    string sql = "REPLACE INTO flight_monitor (workload_key, source, dept_id, dest_id, last_updatetime, last_price, updatetime, price, price_wave) VALUES ";
    ostringstream oss;
    for(MONITOR_DATA::const_iterator it = diff_monitor_data.begin(); it != diff_monitor_data.end(); ++it)
    {
        vector<string> flight_monitor_vec = it->second;
        string workload_key = flight_monitor_vec[0];
        string source = flight_monitor_vec[1];
        string dept_id = flight_monitor_vec[7];
        string dest_id = flight_monitor_vec[8];
        string last_updatetime = flight_monitor_vec[2];
        string last_price = flight_monitor_vec[3];
        string updatetime = flight_monitor_vec[4];
        string price = flight_monitor_vec[5];
        string price_wave = flight_monitor_vec[6];
        oss << "('" << workload_key << "','" << source << "','" << dept_id << "','" << dest_id << "','" << last_updatetime << "','" << last_price << "','" << updatetime << "','" << price << "','" << price_wave << "'),";
    }
    sql += oss.str();
    sql.erase(sql.find_last_of(','), 1);
    // 执行
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
        return false;
    }
    _INFO("UPDATE flight_monitor ok!");
    mysql_close(mysql);
    delete mysql;
    return true;
}

bool TaskMonitor::updateRoomMonitorData(const MONITOR_DATA& diff_monitor_data, const string& host, const string& db, const string& user, const string& passwd)  
{
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }
    // 生成更新sql
    string sql = "REPLACE INTO room_monitor (workload_key, source, last_updatetime, last_price, updatetime, price, price_wave) VALUES ";
    ostringstream oss;
    int num = 1;
    for(MONITOR_DATA::const_iterator it = diff_monitor_data.begin(); it != diff_monitor_data.end(); ++it, num++)
    {
        vector<string> room_monitor_vec = it->second;
        string workload_key = room_monitor_vec[0];
        string source = room_monitor_vec[1];
        //string city = room_monitor_vec[7];
        //string source_hotelid = room_monitor_vec[8];
        string last_updatetime = room_monitor_vec[2];
        string last_price = room_monitor_vec[3];
        string updatetime = room_monitor_vec[4];
        string price = room_monitor_vec[5];
        string price_wave = room_monitor_vec[6];
        oss << "('" << workload_key << "','" << source << "','" << last_updatetime << "','"  << last_price << "','" << updatetime << "','" << price << "','" << price_wave << "'),";
        if(num % 10 == 0)
        {
            sql += oss.str();
            sql.erase(sql.find_last_of(','), 1);
            // 执行
            if(int t = mysql_query(mysql, sql.c_str()) != 0)
            {
                _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
            }
            sql = "REPLACE INTO room_monitor (workload_key, source, last_updatetime, last_price, updatetime, price, price_wave) VALUES ";
            oss.str("");
        }
    }
    sql += oss.str();
    sql.erase(sql.find_last_of(','), 1);
    // 执行
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
    }
    _INFO("UPDATE room_monitor ok!");
    mysql_close(mysql);
    delete mysql;
    return true;
}


string TaskMonitor::serializePrice(const Json::Value& price_value)
{
    Json::FastWriter jfw;
    string str = jfw.write(price_value);
    str = str.erase(str.rfind('\n'));
    return str;
}


bool TaskMonitor::parsePrice(const string& price_str, Json::Value& price_value)
{
    Json::Reader reader;
    return reader.parse(price_str, price_value);
}


float TaskMonitor::getPriceWave(const string& last_price_str, const string& price_str)
{
    // 第一次更新价格，变动无限大
    if("NULL" == last_price_str)
    {
        return 0.999;
    }

    // price解析
    Json::Value last_price_value, price_value;
    if( !parsePrice(last_price_str, last_price_value) || !parsePrice(price_str, price_value) )
    {
        _ERROR("cannot parse price!");
        return 0;
    }
    /*
    if( last_price_value.size() != price_value.size() )
    {
        _ERROR("last_price and price not match!");
        return 0;
    }
    */
    // 计算价格变动
    // 航班ok，如果该航班卖完，则该航班变动为1
    // 按城市抓取的酒店数据只有平均价格和总数，是否需要特殊处理
    float wave = 0.0;
    int num = 0;
    vector<string> last_price_members = last_price_value.getMemberNames();
    for(vector<string>::iterator it = last_price_members.begin(); it != last_price_members.end(); ++it, ++num)
    {
        string key = *it;
        float last_price_item = last_price_value.get(key, 0.0).asDouble();
        float price_item = price_value.get(key, 0.0).asDouble();
        wave += abs(last_price_item - price_item) / max(last_price_item, price_item);
    }
    wave = wave / num;
    return wave;
}
