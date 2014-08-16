#include <sstream>
#include <fstream>
#include <iostream>
#include "common/service_log.hpp"
#include "KeyGenerator.hpp"

KeyGenerator::KeyGenerator()
{
    if( !loadAirport() || !loadFlightSource() || !loadCity() )
    {
        _ERROR("IN keyGenerator: load data error!");
    }
}

KeyGenerator::~KeyGenerator()
{
}


bool KeyGenerator::connect2DB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd)
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

bool KeyGenerator::loadAirport()
{
    // 连接数据库
    string host = "114.215.168.168";
    string db = "basic";
    string user = "root";
    string passwd = "miaoji@2014!";
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }
    // 查询机场信息
    string sql = "SELECT iatacode, city, city_en_name, city_cn_name, city_pinyin FROM airport";
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
                tr1::unordered_map<string, string> airport_map;
                airport_map["airport"] = row[0];
                airport_map["city"] = row[1];
                airport_map["city_en"] = row[2];
                airport_map["city_cn"] = row[3];
                airport_map["city_pinyin"] = row[4];
                m_airport[ row[0] ] = airport_map;
            }
        }
        mysql_free_result(res);
    }

    mysql_close(mysql);
    delete mysql;
    _INFO("IN KeyGenrator, load Airport successfully!");
    return true;
}

bool KeyGenerator::loadFlightSource()
{
    // 连接数据库
    string host = "114.215.168.168";
    string db = "workload";
    string user = "root";
    string passwd = "miaoji@2014!";
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }
    // 查询源的信息
    string sql = "SELECT source_name, workload_rule, workload_spliter, workload_type, source_status, source_class, source FROM workload_flight_source";
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
                tr1::unordered_map<string, string> source_map;
                source_map["name"] = row[0];
                source_map["rule"] = row[1];
                source_map["spliter"] = row[2];
                source_map["type"] = row[3];
                source_map["status"] = row[4];
                source_map["class"] = row[5];
                source_map["source"] = row[6];
                m_flight_source[ row[6] ] = source_map;
            }
        }
        mysql_free_result(res);
    }

    mysql_close(mysql);
    delete mysql;
    _INFO("IN KeyGenrator, load Flight Source successfully!");
    return true;
}

bool KeyGenerator::loadFlightPair()
{
    // 连接数据库
    string host = "114.215.168.168";
    string db = "workload";
    string user = "root";
    string passwd = "miaoji@2014!";
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }
    // 查询航班航线信息
    for(FLIGHT_DATA::iterator it = m_flight_source.begin(); it != m_flight_source.end(); ++it)
    {
        vector< pair<string, string> > pair_vec;
        string source_name = (it->second)["name"];
        ostringstream oss;
        oss << "SELECT dept_airport, dest_airport FROM workload_flight_pair WHERE " << source_name << "=1";
        if(int t = mysql_query(mysql, oss.str().c_str()) != 0)
        {
            _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), oss.str().c_str());
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
                    string dept_airport = row[0];
                    string dest_airport = row[1];
                    pair_vec.push_back( pair<string, string>(dept_airport, dest_airport) );
                    m_flight_pair[source_name] = pair_vec;
                }
            }
            mysql_free_result(res);
        }
    }
    mysql_close(mysql);
    delete mysql;
    _INFO("IN KeyGenrator, load Flight Pair successfully!");
    return true;
}

bool KeyGenerator::loadCity()
{
    // 连接数据库
    string host = "114.215.168.168";
    string db = "basic";
    string user = "root";
    string passwd = "miaoji@2014!";
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        return false;
    }
    // 查询城市信息
    string sql = "SELECT name, name_en, py FROM city_all";
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
                tr1::unordered_map<string, string> city_map;
                city_map["city_name"] = row[0];
                city_map["city_en"] = row[1];
                city_map["city_pinyin"] = row[2];
                m_city[ row[0] ] = city_map;
            }
        }
        mysql_free_result(res);
    }

    mysql_close(mysql);
    delete mysql;
    _INFO("IN KeyGenrator, load City successfully!");
    return true;
}


string KeyGenerator::getKeyFromRule(const string& rule, const string& spliter, const string& type, const string& dept_id, const string& dest_id)
{
    if(type != "oneway" && type != "round")
    {
        _ERROR("IN getKeyFromRule, wrong type!");
        return "";
    }

    string result = "";

    // 分割rule
    vector<string> keys;
    SplitString(rule, "+", &keys);
    // 去除rule中的日期
    (keys).pop_back();
    if(type == "round")
    {
        (keys).pop_back();
    }

    for(vector<string>::iterator it = (keys).begin(); it != (keys).end(); ++it)
    {
        string key = *it;
        if( StringEndsWith(key, "1") )
        {
            key = key.substr(0, key.length()-1);
            result += m_airport[dept_id][key] + spliter;
        }
        else if( StringEndsWith(key, "2") )
        {
            key = key.substr(0, key.length()-1);
            result += m_airport[dest_id][key] + spliter;
        }
        else
        {
            _ERROR("wrong rule!");
        }
    }
    return result;
}

string KeyGenerator::getFlightOnewayKey(const string& source, const string& dept_id, const string& dest_id, const string& dept_day)
{
    string rule = m_flight_source[source]["rule"];
    string spliter = m_flight_source[source]["spliter"];
    string type = m_flight_source[source]["type"];
    string workload_key = getKeyFromRule(rule, spliter, type, dept_id, dest_id);
    workload_key += dept_day;
    return workload_key;
}

string KeyGenerator::getFlightRoundKey(const string& source, const string& dept_id, const string& dest_id, const string& dept_day, const string& dest_day)
{
    string rule = m_flight_source[source]["rule"];
    string spliter = m_flight_source[source]["spliter"];
    string type = m_flight_source[source]["type"];
    string workload_key = getKeyFromRule(rule, spliter, type, dept_id, dest_id);
    workload_key += dept_day;
    workload_key += spliter + dest_day;
    return workload_key;
}

string KeyGenerator::getRoomKey(const string& source, const string& city_name, const string& hotel_id, const string& checkin_day, const string& checkout_day)
{
    // 城市英文名
    string city_en = m_city[city_name]["city_en"];
    // 计算入住日期
    time_t checkin_seconds = DateTime::Parse(checkin_day, "yyyyMMdd").GetSecondsSinceEpoch();
    time_t checkout_seconds = DateTime::Parse(checkout_day, "yyyyMMdd").GetSecondsSinceEpoch();
    int days = (int(checkout_seconds) - int(checkin_seconds)) / 86400;
    
    // 按酒店规则生成workload_key
    ostringstream oss;
    oss << source << "&" << city_en << "&" << hotel_id << "&" << days << "&" << checkin_day;
    return oss.str();
}
