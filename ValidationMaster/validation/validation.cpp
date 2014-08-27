#include "common/service_log.hpp"
#include "common/string/algorithm.h"
#include "CommonFuc.h"
#include "validation.hpp"
using namespace std;


Validation::Validation()
{
    m_client = new SocketClient();
    loadHotelWorkload("114.215.168.168", "workload", "root", "miaoji@2014!");
}


Validation::~Validation()
{
    delete m_client;
}


void Validation::registerSlave(const string& ip, bool recv_realtime_req)
{
    //收到slave的ip
    if(recv_realtime_req)
    {
        m_slaves.insert(ip);
    }
}


bool Validation::handleValidReq(const string& req, const string& type, string& res)
{
    vector<string> vec;
    SplitString(req, "|", &vec);
    if(type == "flight")
    {
        //航班验证
        if(vec.size() != 6)
            return false;
        string source = vec[5];
        source += "Flight";
        string flight_req = "validate?req=" + COMMON::url_encode(req) + "&source=" + COMMON::url_encode(source);
        repostValidReq(flight_req, res);
    }
    else if(type == "hotel")
    {
        // 酒店验证
        if(vec.size() != 7)
            return false;
        string source = vec[6];
        string hotel_workload_key = vec[0] + "|" + vec[1] + "|" + vec[6] + "Hotel";
        string hotel_workload_content = "";
        if( m_hotel_data.find(hotel_workload_key) != m_hotel_data.end() )
            hotel_workload_content = m_hotel_data[hotel_workload_key];
        string hotel_validation_content = hotel_workload_content + "&" + vec[2] + "&" + vec[3] + "|" + vec[4] + "|" + vec[5] + "|" + source;
        string hotel_req = "validate?req=" + COMMON::url_encode(req) + "&source=" + COMMON::url_encode(source);
        repostValidReq(hotel_req, res);
    }
    else
    {
        return false;
    }
}


bool Validation::repostValidReq(const string& req, string& slave_res)
{
    // 随机选择一个可用slave, 并转发请求 
    srand(time(NULL));
    int slave_index = rand() % m_slaves.size();
    int num = 0;
    for(tr1::unordered_set<string>::iterator it = m_slaves.begin(); it != m_slaves.end(); ++it, num++)
    {
        if(num != slave_index)
            continue;
        string slave_ip = (*it);
        cout << slave_ip << endl;
        m_client->init(slave_ip, 100000000);
        //m_client->init("112.124.18.14:8088", 1000000);
        ServerRst server_rst;
        cout << req << endl;
        m_client->getRstFromHost(req, server_rst, 0);
        //m_client->getRstFromHost("heartbeat?request_task_num=0&error_task_num=1029&thread_num=20&process_task_num=2718&id=1037", server_rst, 0);
        slave_res = server_rst.ret_str;
    }
    return true;
}


bool Validation::loadHotelWorkload(const string& host, const string& db, const string& user, const string& passwd)
{
    MYSQL* mysql = (MYSQL*)malloc(sizeof(MYSQL));
    string sql = "SELECT workload_key, content FROM workload_hotel";
    if( !connect2DB(mysql, host, db, user, passwd) )
    {
        _ERROR("[IN loadHotelWorkload, connect db error: %s]",  mysql_error(mysql));
    }
    if(int t = mysql_query(mysql, sql.c_str()) != 0)
    {
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(mysql), sql.c_str());
        mysql_close(mysql);
        delete mysql;
        return false;
    }
    else
    {
        MYSQL_RES* res = mysql_use_result(mysql);
        MYSQL_ROW row;
        if(res)
        {
            while(row = mysql_fetch_row(res))
            {
                string workload_key = row[0];
                string content = row[1];
                if(workload_key != "" && content != "")
                    m_hotel_data[workload_key] = content;
            }
        }
        mysql_free_result(res);
        mysql_close(mysql);
        delete mysql;
        return true;
    }
}


bool Validation::connect2DB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd)
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
