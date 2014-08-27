#ifndef _VALIDATION_HPP
#define _VALIDATION_HPP

#include <string>
#include <vector>
#include <tr1/unordered_set>
#include <tr1/unordered_map>
#include <mysql/mysql.h>
#include "CommonFuc.hpp"
#include "../Client/SocketClient.h"
using namespace std;


class Validation
{
    public:
        Validation();
        ~Validation();
        bool selectSlaveIp(const tr1::unordered_set<string>& slave_list);
        bool handleValidReq(const string& req, const string& type, string& res);
        bool repostValidReq(const string& req, string& res);
    
    private:
        bool loadHotelWorkload(const string& host, const string& db, const string& user, const string& passwd);
        bool connect2DB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd);

    private:
        SocketClient* m_client;                 // 向slave发送验证请求的客户端
        string m_slave_ip;                      // 可用的slave的ip和端口
        tr1::unordered_map<string, string> m_hotel_data;
};

#endif // _VALIDATION_HPP
