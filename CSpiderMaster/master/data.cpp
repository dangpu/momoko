#include "data.hpp"
#include "common/time/datetime.h"
using namespace std;


//static bool Task::parse(const string& task_str, vector<Task>& tasks);

string SlaveInfo::str()
{
    // 初始化Json::Value
    Json::Value value;
    value["id"] = m_id;
    value["name"] = m_name;
    value["server"] = m_server;
    value["path"] = m_path;
    value["server_ip"] = m_server_ip;
    value["start_time"] = (int)m_start_time;
    value["thread_num"] = m_thread_num;
    value["process_task_num"] = m_process_task_num;
    value["error_task_num"] = m_error_task_num;
    value["type"] = m_type;
    value["last_heartbeat"] = (int)m_last_heartbeat;
    value["status"] = m_status;
    value["request_task_num"] = m_request_task_num;
    value["recv_realtime_req"] = m_recv_realtime_req;

    // 序列化
    Json::FastWriter jfw;
    string str = jfw.write(value);
    str = str.erase(str.rfind('\n'));
    return str;
}

bool SlaveInfo::parse(const string& slave_str)
{
    Json::Value value;
    Json::Reader reader;
    if(reader.parse(slave_str, value))
    {
        m_id = value["id"].asString();
        m_name = value["name"].asString();
        m_server = value["server"].asString();
        m_path = value["path"].asString();
        m_server_ip = value["server_ip"].asString();
        m_start_time = (time_t)value["start_time"].asInt();
        m_thread_num = value["thread_num"].asInt();
        m_process_task_num = value["process_task_num"].asInt();
        m_error_task_num = value["error_task_num"].asInt();
        m_type = value["type"].asString();
        m_last_heartbeat = (time_t)value["last_heartbeat"].asInt();
        m_status = value["status"].asInt();
        m_request_task_num = value["request_task_num"].asInt();
        m_recv_realtime_req = value["recv_realtime_req"].asBool();
    }
    return true;
}


string Task::str()
{
    // 初始化Json::Value
    Json::Value value;
    value["id"] = m_id;
    value["workload_key"] = m_workload_key;
    value["content"] = m_content;
    value["source"] = m_source;
    value["priority"] = m_priority;
    value["score"] = m_score;
    value["timeslot"] = m_timeslot;
    value["is_assigned"] = m_is_assigned;
    value["update_times"] = m_update_times;
    value["success_times"] = m_success_times;
    value["error"] = m_error;

    // 序列化
    Json::FastWriter jfw;
    string str = jfw.write(value);
    str = str.erase(str.rfind('\n'));
    return str;
}

bool Task::parse(const string& task_str, vector<Task*>& tasks)
{
    Json::Value value1;
    Json::Reader reader;
    string str = task_str;
    if(reader.parse(str, value1))
    {
        for(Json::Value::iterator it = value1.begin(); it != value1.end(); ++it)
        {
            Task * task = new Task();
            Json::Value value = *it;
            if(value.isMember("id")){
                task->m_id = value["id"].asString();
	    }
            if(value.isMember("workload_key")){
		if(value["workload_key"].isString())
		{
                	task->m_workload_key = value["workload_key"].asString();
		}
	    }
            if(value.isMember("content"))
                task->m_content = value["content"].asString();
            if(value.isMember("source"))
                task->m_source = value["source"].asString();
            if(value.isMember("priority"))
                task->m_priority = value["priority"].asInt();
            if(value.isMember("score"))
                task->m_score = value["score"].asInt();
            if(value.isMember("timeslot"))
                task->m_timeslot = value["timeslot"].asInt();
            if(value.isMember("is_assigned"))
                task->m_is_assigned = value["is_assigned"].asInt();
            if(value.isMember("update_times"))
                task->m_update_times = value["update_times"].asInt();
            if(value.isMember("success_times"))
                task->m_success_times = value["success_times"].asInt();
            if(value.isMember("error"))
                task->m_error = value["error"].asInt();
            
            tasks.push_back(task);
        }
	//_INFO("[TASK SIZE IS %s]", tasks.size());
    }
    return true;
}
/*
bool Task::parse(const string& task_str)
{
    Json::Value value;
    Json::Reader reader;
    string str = task_str;
    if(task_str[0]=='[' && task_str[task_str.length()-1]==']')
    {
        str = task_str.substr(1, task_str.length()-2);
    }
    
    if(reader.parse(str, value))
    {
        if(value.isMember("id"))
            m_id = value["id"].asString();
        if(value.isMember("workload_key"))
            m_workload_key = value["workload_key"].asString();
        if(value.isMember("content"))
            m_content = value["content"].asString();
        if(value.isMember("source"))
            m_source = value["source"].asString();
        if(value.isMember("priority"))
            m_priority = value["priority"].asInt();
        if(value.isMember("score"))
            m_score = value["score"].asInt();
        if(value.isMember("timeslot"))
            m_timeslot = value["timeslot"].asInt();
        if(value.isMember("is_assigned"))
            m_is_assigned = value["is_assigned"].asInt();
        if(value.isMember("update_times"))
            m_update_times = value["update_times"].asInt();
        if(value.isMember("success_times"))
            m_success_times = value["success_times"].asInt();
        if(value.isMember("error"))
            m_error = value["error"].asInt();
    }
    return true;
}
*/
