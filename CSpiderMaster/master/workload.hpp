#ifndef _WORKLOAD_HPP_
#define _WORKLOAD_HPP_

/*
 * AUTHOR: zhangyang
 * DATE: 2014.7.18
 * DESC: 
 *      获得workload
 *      每一个INTERVAL内抓去一次workload
 *      每一批的执行情况写入数据库
 *      slave处理完毕后抓去长期任务
 *      抓取不完则丢弃
 */

#include <string>
#include <vector>
#include <tr1/unordered_map>
#include <tr1/unordered_set>
#include <mysql/mysql.h>
#include <pthread.h>
#include "common/time/datetime.h"
#include "CommonFuc.hpp"
#include "data.hpp"
using namespace std;

typedef tr1::unordered_set<string> STRING_SET;
typedef tr1::unordered_map<string, Task> TASK_MAP;
typedef tr1::unordered_map< string, vector<string> > STRING_MAP;

class WorkloadMaster
{
    private:
        WorkloadMaster();
        ~WorkloadMaster();

    private:
        static WorkloadMaster* m_pInstance;

    public:
        static WorkloadMaster* getInstance()
        {
            if(NULL == m_pInstance)
                m_pInstance = new WorkloadMaster();
            return m_pInstance;
        }

    public:
        
        bool connectDB(MYSQL* mysql, const string& host, const string& db, const string& user, const string& passwd);
        
        /* 执行sql语句，从数据库中读取任务
         * @param sql: sql语句
         * @param tasks: 读取的任务
         */
        bool getTasksBySQL(const string& sql, TASK_MAP& tasks);
        
        /* 读取长期任务
         * @param tasks: 读取的长期任务
         */
        bool getLongtermTasks(TASK_MAP& tasks);
        bool getTask(Task& task);
        bool getTasks(vector<Task*>& tasks, int count);
        
        /* 定时从数据库中读取数据，并写入监控信息，定时由外部请求触发
         */
        void updateWorkload();
        
        /* 响应slave请求，分配一个任务，返回json格式
         * @param source: 只取该source的任务
         */
        string assignTask(const string& source, int count);

        /* 响应slave请求，完成任务
         * @param: json格式的task
         */
        void completeTask(const string& task);

        void completeTask(const string& workload_key, int error);

        /* 禁用源
         */
        void addForbiddenSource(const string& source);
        
        /* 解禁源
         */
        void delForbiddenSource(const string& source);

        /* 监控任务执行情况，写入workload_monitor数据库
         * @param: timeslot 相应的时间槽
         */
        void monitorTasks(int timeslot);

    private:
        bool executeSQL(const string& sql);
        bool updateUpdateTimes(const string& worklaod_key);
        bool updateSuccessTimes(const string& workload_key);
        bool updateFailedTimes(const string& workload_key);
        

    public:
        STRING_SET m_forbidden_sources;         // 不抓取的source
        int m_status;                           // 1代表常规任务已抓去完成
        TASK_MAP m_tasks;                       // 所有任务
        STRING_MAP m_task_status;               // 每个任务的key和该任务的执行情况
        //MYSQL* m_mysql;                         // 数据库
        pthread_mutex_t m_locker;               // 线程锁
        DateTime m_today;                       // 日期
        int m_task_num;
};
#endif  // WORKLOAD_HPP
