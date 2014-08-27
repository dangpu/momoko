#ifndef _MASTER_HPP_
#define _MASTER_HPP_

/*
 * AUTHOR: zhangyang
 * DATE: 2014.7.17
 * DESC: 定义master类型
 */

#include <string>
#include <tr1/unordered_map>
#include <tr1/unordered_set>
#include "CommonFuc.hpp"
#include "data.hpp"
#include "validation.hpp"
using namespace std;

//class Master;

class Master
{
    private:
        Master();
        ~Master();
    private:
        static Master* m_pInstance;

    public:
        static Master* getInstance()
        {
            if(NULL == m_pInstance)
                m_pInstance = new Master();
            return m_pInstance;
        }

        static void release()
        {
            if(NULL != m_pInstance)
            {
                delete m_pInstance;
                m_pInstance = NULL;
            }
        }

        //bool init(const string& host, const string& port);

        /* 处理slave的心跳请求
         * @param slave_id: slave id
         * @param thread_num: 运行的线程数目
         * @param process_task_num: 总共执行的任务数目
         * @param error_task_num: 出错的任务数目
         * @param request_task_num: 实时请求的任务数目
         */
        bool heartbeat(const string& slave_id, int thread_num, int process_task_num, int error_task_num, int request_task_num);

        /* 处理一个新slave的注册请求，分配一个id给slave
         * @param slave_name: slave名称
         * @param server: slave ip
         * @param path: slave所在机器路径
         * @param server_ip: 提供服务的地址及端口，供实时请求使用
         * @param type: slave类型
         * @param recv_realtime_req: 是否接收实时请求
         */
        string registerSlave(const string& slave_name, const string& server, const string& path, const string& server_ip, const string& type, bool recv_realtime_req);

        /* 返回特定id的slave状态
         * @param slave_id: slave id
         */
        string getStatus(const string& slave_id);

        /* 修改slave运行的线程数目
         * @param slave_id: 线程id
         * @param thread_num: 线程数目
         */
        string modifyThreadNum(const string& slave_id, int thread_num);

        /* 监控slave状态信息，并写入文件
         */
        void monitorSlave();

        /* 随机获得一个可用于接收实时请求的slave
         */
        SlaveInfo getRealtimeSlave();

        /* 获取所有的slave信息
         */
        tr1::unordered_map<string, SlaveInfo> getSlaves()
        {
            return m_slave_map;
        }

        /* 验证
         * @param req, 待验证请求
         * @param type, 验证请求类型
         * @return, 请求返回内容
         */
        string validate(const string& req, const string& type);

    public:
        // 所有slave信息
        tr1::unordered_map<string, SlaveInfo> m_slave_map;
        // 可以接收实时请求的slave列表
        tr1::unordered_set<string> m_slave_list;
        string m_last_id;
        pthread_mutex_t m_locker;

        Validation* m_validation_master;

};

#endif  // MASTER_HPP
