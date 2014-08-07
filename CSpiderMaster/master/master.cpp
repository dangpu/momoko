#include "master.hpp"
using namespace std;

#define MONITOR_FILE "monitor_file.dat"

Master* Master::m_pInstance = NULL;

Master::Master()
{
    m_last_id = "0";
    m_locker = PTHREAD_MUTEX_INITIALIZER;
}

Master::~Master()
{
    release();
}

string Master::registerSlave(const string& slave_name, const string& server, const string& path, const string& server_ip, const string& type, bool recv_realtime_req)
{
    pthread_mutex_lock(&m_locker);
    
    // slave信息
    SlaveInfo slave_info;
    slave_info.m_name = slave_name;
    slave_info.m_server = server;
    slave_info.m_path = path;
    slave_info.m_server_ip = server_ip;
    slave_info.m_type = type;
    slave_info.m_recv_realtime_req = recv_realtime_req;
    slave_info.m_status = 1;
    DateTime datetime;
    slave_info.m_start_time = datetime.GetSecondsSinceEpoch();
    slave_info.m_last_heartbeat = datetime.GetSecondsSinceEpoch();

    // 分配id
    ostringstream oss;
    oss << atoi(m_last_id.c_str()) + 1;
    string id = oss.str();
    m_last_id = id;
    slave_info.m_id = id;
    m_slave_map[id] = slave_info;
    

    if(recv_realtime_req)
        m_slave_list.insert(id);
    pthread_mutex_unlock(&m_locker);
    return id;
}


bool Master::heartbeat(const string& slave_id, int thread_num, int process_task_num, int error_task_num, int request_task_num)
{
    tr1::unordered_map<string, SlaveInfo>::iterator it = m_slave_map.find(slave_id);
    if(it != m_slave_map.end())
    {
        pthread_mutex_lock(&m_locker);
        SlaveInfo slave_info = it->second;
        slave_info.m_id = slave_id;
        slave_info.m_thread_num = thread_num;
        slave_info.m_process_task_num = process_task_num;
        slave_info.m_error_task_num = error_task_num;
        slave_info.m_request_task_num = request_task_num;
        DateTime datetime;
        slave_info.m_last_heartbeat = datetime.GetSecondsSinceEpoch();
        pthread_mutex_unlock(&m_locker);
        return true;
    }
    else
    {
        return false;
    }
}


string Master::getStatus(const string& slave_id)
{
    tr1::unordered_map<string, SlaveInfo>::iterator it = m_slave_map.find(slave_id);
    if("NULL" != slave_id && it != m_slave_map.end())
    {   
        // 取得特定id的slave信息
        SlaveInfo slave_info = it->second;
        return slave_info.str();
    }
    else
    {
        // 若id未制定，获取所有slave信息
        string results = "[";
        for(it = m_slave_map.begin(); it != m_slave_map.end(); ++it)
        {
            results += it->second.str() + ",";
        }
        results += "]";
        return results;
    }
}


string Master::modifyThreadNum(const string& slave_id, int thread_num)
{
    // 貌似现在未使用
    ;
}

// realtime slave其实也没启用
SlaveInfo Master::getRealtimeSlave()
{
    // 随机返回一个slave
    srand( (unsigned)time(NULL) );
    int random_index = rand() % m_slave_list.size();
    tr1::unordered_set<string>::iterator it = m_slave_list.begin();
    int num = 0;
    for(; it != m_slave_list.end(); ++it, ++num)
    {
        if(num == random_index)
            return m_slave_map.find(*it)->second;
    }
}


void Master::monitorSlave()
{
    ofstream out(MONITOR_FILE);
    DateTime datetime;
    time_t now = datetime.GetSecondsSinceEpoch();
    for(tr1::unordered_map<string, SlaveInfo>::iterator it = m_slave_map.begin(); it != m_slave_map.end(); ++it)
    {
        pthread_mutex_lock(&m_locker);
        if(now - it->second.m_last_heartbeat >= 10*60)
        {
            // 超过60分钟没有心跳信息，删除slave
            m_slave_map.erase(it);
            out << it->second.str();
        }
        else if(now - it->second.m_last_heartbeat >= 2*60)
        {
            // 超过5分钟没有心跳信息，则不可用
            it->second.m_status = -1;
        }
        pthread_mutex_unlock(&m_locker);
    }
    out.close();
}
