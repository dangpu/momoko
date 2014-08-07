#ifndef _DATA_HPP_
#define _DATA_HPP_

/*
 * AUTHOR: zhangyang
 * DATE: 2014.7.17
 * DESC: 定义需要与slave交互的数据类型
 *          1. SlaveInfo，slave信息
 *          2. Task，任务信息
 */


#include <string>
#include <vector>
#include <iostream>
#include <tr1/unordered_map>
#include <tr1/unordered_set>
#include "json/json.h"
#include "common/service_log.hpp"
#include "common/time/datetime.h"
using namespace std;

/*
class SlaveInfo;
class Task;
typedef tr1::unordered_set<SlaveInfo> SLAVE_SET;
typedef tr1::unordered_set<Task> TASK_SET;
*/

class SlaveInfo
{
    public:
        SlaveInfo()
        {
            m_id = "NULL";
            m_name = "NULL";
            m_server = "NULL";
            m_path = "NULL";
            m_server_ip = "NULL";
            m_start_time = 0;
            m_thread_num = 0;
            m_process_task_num = 0;
            m_error_task_num = 0;
            m_type = "NULL";
            m_last_heartbeat = 0;
            m_status = 0;
            m_request_task_num = 0;
            m_recv_realtime_req = false;
        }
        ~SlaveInfo() {}
        /*
        bool operator <(const SlaveInfo& si) const
        {
            return true;
        }
        */
        /*
        bool operator ==(const SlaveInfo& si) const
        {
            return true;
        }
        */

        /* 调用Json::Writer，实现序列化
         */
        string str();

        /* 调用Json::Reader, 实现解析
         */
        bool parse(const string& slave_str);

    public:
        string m_id;                // slave id
        string m_name;              // slave 名称
        string m_server;            // slave 所在机器的ip
        string m_path;              // slave 所在机器的路径
        string m_server_ip;         // 提供服务的地址，包括端口号，供real_time_request使用
        time_t m_start_time;        // 开始运行时间
        int m_thread_num;           // 运行线程数目
        int m_process_task_num;     // 总共处理task数目
        int m_error_task_num;       // 错误task总数目
        string m_type;              // slave 类型
        time_t m_last_heartbeat;    // 最近一次上报心跳信息时间
        int m_status;               // 状态，1表示正常，-1表示丢失连接
        int m_request_task_num;     // 实时连接的task数目
        bool m_recv_realtime_req;   // 是否允许接收实时请求

};

class Task
{
    public:
        Task()
        {
            m_id = "NULL";
            m_workload_key = "NULL";
            m_content = "NULL";
            m_source = "NULL";
            m_priority = 0;
            m_score = 0;
            m_timeslot = 0;
            m_is_assigned = 0;
            m_update_times = 0;
            m_success_times = 0;
            m_error = -1;
        }
        
        Task(const Task& task)
        {
            m_id = task.m_id;
            m_workload_key = task.m_workload_key;
            m_content = task.m_content;
            m_source = task.m_source;
            m_priority = task.m_priority;
            m_score = task.m_score;
            m_timeslot = task.m_timeslot;
            m_is_assigned = task.m_is_assigned;
            m_update_times = task.m_update_times;
            m_success_times = task.m_success_times;
            m_error = task.m_error;
            //_INFO("[ZHANGYANG, COPY CONSTRUCTION!]");
        }

        ~Task() {}

        /* 返回序列化的任务对象
         */
        string str();

        /* 返回Task对象
         */
        static bool parse(const string& task_str, vector<Task*>& tasks);

    public:
        string m_id;                //
        string m_workload_key;      // 
        string m_content;           // 任务内容，各source不同
        string m_source;            // 任务来源，标示不同的parser
        int m_priority;             // 任务优先级，用来分配时间槽，同一批任务无区别
        int m_score;                // 得分，得分高的在一批任务中优先抓取
        int m_timeslot;             // 被分配到的时间槽
        int m_is_assigned;          // 是否被分配
        int m_update_times;         // 抓取次数
        int m_success_times;        // 抓取成功次数
        int m_error;                // 错误代码
};

#endif	// DATA_HPP
