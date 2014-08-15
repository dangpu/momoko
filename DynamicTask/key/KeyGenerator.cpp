#include <sstream>
#include <fstream>
#include <iostream>
#include "common/service_log.hpp"
#include "common/string/algorithm.h"
#include "KeyGenerator.hpp"

KeyGenerator::KeyGenerator()
{
    if( !loadAirport() || !loadFlightSource() || !loadFlightPair() )
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
    string sql = "select iatacode, city, city_en_name, city_cn_name, city_pinyin from airport";
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
                tr1::unordered_map<string> airport_map;
                airport_map["airport"] = row[0];
                airport_map["city"] = row[1];
                airport_map["city_en"] = row[2];
                airport_map["city_cn"] = row[3];
                airport_map["city_pinyin"] = row[4];
            }
            m_airport[ row[0] ] = airport_map;
        }
        mysql_free_result(res);
    }

    mysql_close(mysql);
    delete m_mysql;
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
    string sql = "SELECT source_name, workload_rule, workload_spliter, workload_type, source_status, source_class FROM workload_flight_source";
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
                tr1::unordered_map<string> source_map;
                source_map["name"] = row[0];
                source_map["rule"] = row[1];
                source_map["spliter"] = row[2];
                source_map["type"] = row[3];
                source_map["status"] = row[4];
                source_map["class"] = row[5];
            }
            m_flight_source[ row[0] ] = source_map;
        }
        mysql_free_result(res);
    }

    mysql_close(mysql);
    delete m_mysql;
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
        string source_name = it->first;
        ostringstream oss;
        oss << "SELECT dept_airport, dest_airport FROM workload_flight_pair WHERE " << source_name << "=1";
        if(int t = mysql_query(mysql, oss.str().c_str()) != 0)
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
                    string dpet_airport = row[0];
                    string dest_airport = row[1];
                    pair_vec.push_back( pair<string, string>(dept_airport, dest_airport) );
                }
                m_flight_pair[source_name] = pair_vec;
            }
        }
        mysql_free_result(res);
    }
    mysql_close(mysql);
    delete mysql;
    return true;
}


string KeyGenerator::getKeyFromRule(const string& rule, const string& spliter, const string& type, const string& dept_id, const string& dest_id)
{
    if(type != "oneway" && type != "round")
    {
        _ERROR("IN getKeyFromRule, wrong type!");
        return "";
    }

    string result;

    // 分割rule
    vector<string> keys;
    SplitString(rule, spliter.c_str(), keys);
    // 去除rule中的日期
    keys.pop_back();
    if(type == "round")
    {
        keys.pop_back();
    }

    for(vector<string>::iterator it = keys.begin(); it != keys.end(); ++it)
    {
        string key = *it
        if( StringEndsWith(key, "1") )
        {
            key = key.substr(0, key.length()-1);
            result += m_airport[key] + spliter;
        }
        else if( StringEndsWith(key, "2") )
        {
            key = key.substr(0, key.length()-1);
            result += m_airport[key] + spliter;
        }
    }
    return result;
}

string KeyGenerator::getFlightOnewayKey(const string& source, const string& dept_id, const string& dest_id, const string& dept_day)
{
    string rule = m_flight_source[source]["rule"];
    string spliter = m_flight_source[source]["spliter"];
    string workload_key = getKeyFromRule(rule, spliter, dest_id, dept_id);
    workload_key += dept_day;
    return workload_key;
}

string KeyGenerator::getFlightRoundKey(const string& source, const string& dept_id, const string& dest_id, const string& dept_day, const string& dest_day)
{
    string rule = m_flight_source[source]["rule"];
    string spliter = m_flight_source[source]["spliter"];
    string workload_key = getKeyFromRule(rule, spliter, dest_id, dept_id);
    workload_key += dept_day;
    workload_key += spliter + dest_day;
    return workload_key;
}

string getRoomKey(const string& source, const string& city_name, const string& hotel_id, const string& checkin_day, const string& checkout_day)
{
    string city_en = m_city[city_name];
    int days = 
}
