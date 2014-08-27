#include <sstream>
#include "common/service_log.hpp"
#include "workload.hpp"
using namespace std;

// 定义取workload的时间间隔，单位：分钟
#define INTERVAL 5

WorkloadMaster* WorkloadMaster::m_pInstance = NULL;

WorkloadMaster::WorkloadMaster()
{
    m_task_num = 0;
    m_status = 0;
    m_locker = PTHREAD_MUTEX_INITIALIZER;
    m_today = DateTime::Today();
}

WorkloadMaster::~WorkloadMaster()
{
    m_forbidden_sources.clear();
    m_tasks.clear();
    m_task_status.clear();
}

void WorkloadMaster::updateWorkload()
{
    pthread_mutex_lock(&m_locker);

    // 分配时间槽
    DateTime now = DateTime::Now();
    int hour = now.GetHour();
    int minute = now.GetMinute();
    int timeslot = (hour*60+minute) / INTERVAL;
    m_today = DateTime::Today();

    // 将上一时间槽的任务监控写入数据库
    monitorTasks(timeslot);
    m_status = 0;

    // 取新任务
    ostringstream oss;
    oss << "SELECT workload_key, content, source FROM workload_" << m_today.ToString(string("yyyyMMdd")) << " WHERE timeslot = " << timeslot;
    //oss << "SELECT workload_key, content, source FROM workload_" << m_today.ToString(string("yyyyMMdd")) << " WHERE timeslot = " << timeslot << " or timeslot = " << timeslot+1;
    string sql = oss.str();
    // 清空task任务和状态
    m_tasks.clear();
    m_task_status.clear();
    getTasksBySQL(sql, m_tasks);
    m_task_num = m_tasks.size();
    TASK_MAP::iterator it = m_tasks.begin();
    for(; it != m_tasks.end(); ++it)
    {
        // 初始化m_task_status
        vector<string> status;
        status.push_back("0");
        status.push_back("0");
        status.push_back("-1");
        status.push_back(it->second.m_content);
        status.push_back(it->second.m_source);
        m_task_status[it->second.m_workload_key] = status;
    }

    pthread_mutex_unlock(&m_locker);
}


bool WorkloadMaster::connectDB(MYSQL* m_mysql, const string& host, const string& db, const string& user, const string& passwd)
{
    mysql_init(m_mysql);
    if (!mysql_real_connect(m_mysql, host.c_str(), user.c_str(), passwd.c_str(), db.c_str(), 0, NULL, 0))
    {
        _ERROR("[Connect to %s error: %s]", db.c_str(), mysql_error(m_mysql));
        return false;
    }
    // 设置字符编码
    if (mysql_set_character_set(m_mysql, "utf8"))
    {
        _ERROR("[Set mysql characterset: %s]", mysql_error(m_mysql));
        return false;
    }
    return true;
}


bool WorkloadMaster::executeSQL(const string& sql)
{
    MYSQL* m_mysql = (MYSQL*)malloc(sizeof(MYSQL));
    connectDB(m_mysql, "114.215.168.168", "workload", "root", "miaoji@2014!");
    int t = mysql_query(m_mysql, sql.c_str());
    if(t != 0)
    {
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(m_mysql), sql.c_str());
        mysql_close(m_mysql);
        return false;
    }
    mysql_close(m_mysql);
    delete m_mysql;
    return true;
}

bool WorkloadMaster::getTasksBySQL(const string& sql, TASK_MAP& tasks)
{
    MYSQL* m_mysql = (MYSQL*)malloc(sizeof(MYSQL));
    connectDB(m_mysql, "114.215.168.168", "workload", "root", "miaoji@2014!");
    // 查询数据库
    if(int t = mysql_query(m_mysql, sql.c_str()) != 0)
    {
        _ERROR("[mysql_query error: %s] [error sql: %s]", mysql_error(m_mysql), sql.c_str());
        mysql_close(m_mysql);
        delete m_mysql;
        return false;
    }
    else
    {
        MYSQL_RES* res = mysql_use_result(m_mysql);
        MYSQL_ROW row;
        if(res)
        {
            while(row = mysql_fetch_row(res))
            {
                //if(sizeof(row)/sizeof(row[0]) != 3)
                //    continue;
                Task task;
                task.m_workload_key = row[0];
                task.m_content = row[1];
                task.m_source = row[2];
                tasks.insert( pair<string, Task>(row[0], task) );
            }
        }
        mysql_free_result(res);
        mysql_close(m_mysql);
        delete m_mysql;
        return true;
    }
}


bool WorkloadMaster::getLongtermTasks(TASK_MAP& tasks)
{
    // 随机控制
    srand(time(NULL));
    int j = rand() % 45;

    if(j < 40)
    {
        // 31天到70天随机选择一天
        srand(time(NULL));
        int i = (rand() % 40) + 31;
        TimeSpan ts = TimeSpan(i, 0, 0, 0);
        DateTime dt = m_today+ts;
        ostringstream oss;
        oss << "SELECT workload_key, content, source FROM workload_longterm WHERE crawl_day = " << dt.ToString(string("yyyyMMdd"));
        string longterm_sql = oss.str();
        return getTasksBySQL(longterm_sql, tasks);
    }
    else
    {
        // 另一种方式，5到10天
        srand(time(NULL));
        int i = (rand() % 5) + 6;
        TimeSpan ts = TimeSpan(i, 0, 0, 0);
        DateTime dt = m_today+ts;
        ostringstream oss;
        //oss << "SELECT workload_key, content, source FROM workload_longterm WHERE priority = " << 1 << " and id like '%" << j << "'";
        oss << "SELECT workload_key, content, source FROM workload_longterm WHERE crawl_day = " << dt.ToString(string("yyyyMMdd"));
        string longterm_sql = oss.str();
        return getTasksBySQL(longterm_sql, tasks);
    }
}


bool WorkloadMaster::getTasks(vector<Task*>& tasks, int count)
{
    // 统计可分配的任务，可以改为成员变量
    int tasks_size = 0;
    for(TASK_MAP::iterator it = m_tasks.begin(); it != m_tasks.end(); ++it)
    {
        if( (it->second).m_is_assigned != 1 && m_forbidden_sources.find((it->second).m_source) == m_forbidden_sources.end() )
            tasks_size++;
    }
    // 未实现随机取
    if(tasks_size >= count)
    {
        int num = 0;

        for(TASK_MAP::iterator it = m_tasks.begin(); it != m_tasks.end() && num < count; ++it)
        {
            if( (it->second).m_is_assigned == 1 || m_forbidden_sources.find((it->second).m_source) != m_forbidden_sources.end() )
                continue;
            Task *task = new Task();
            task = &(it->second);
            tasks.push_back(task);
            num++;
            //m_tasks.erase(it);
            m_tasks[it->first].m_is_assigned = 1;
        }
        return true;
    }
    else if(tasks_size < count)
    {
        m_status = 1;
        getLongtermTasks(m_tasks);
        for(TASK_MAP::iterator it = m_tasks.begin(); it != m_tasks.end(); ++it)
        {
            vector<string> status_set;
            status_set.push_back("0");
            status_set.push_back("0");
            status_set.push_back("-1");
            status_set.push_back(it->second.m_content);
            status_set.push_back(it->second.m_source);
            m_task_status.insert( pair<string, vector<string> >(it->second.m_workload_key, status_set) );
        }
        int num = 0;
        for(TASK_MAP::iterator it = m_tasks.begin(); it != m_tasks.end() && num < count; ++it)
        {
            if( (it->second).m_is_assigned == 1 || m_forbidden_sources.find((it->second).m_source) != m_forbidden_sources.end() )
                continue;
            Task *task = new Task();
            task = &(it->second);
            tasks.push_back(task);
            num++;
            //m_tasks.erase(it);
            m_tasks[it->first].m_is_assigned = 1;
        }
        return true;
    }
}

bool WorkloadMaster::getTask(Task& task)
{
    // 统计未被分配的任务，可以改为成员变量
    int tasks_size = 0;
    for(TASK_MAP::iterator it = m_tasks.begin(); it != m_tasks.end(); ++it)
    {
        if( (it->second).m_is_assigned != 1 && m_forbidden_sources.find((it->second).m_source) == m_forbidden_sources.end() )
            tasks_size++;
    }
    
    if(tasks_size > 0)
    {
        // 常规任务没取完
        srand(time(NULL));
        int i = rand() % m_tasks.size();
        TASK_MAP::iterator it = m_tasks.begin();
        int num = 0;
        for(; it != m_tasks.end(); ++it, ++num)
        {
            if( (it->second).m_is_assigned == 1 || m_forbidden_sources.find((it->second).m_source) != m_forbidden_sources.end() )
                continue;
            if(num == i)
            {
                task = it->second;
                //m_tasks.erase(it);
                m_tasks[it->first].m_is_assigned = 1;
            }
        }
    }
    else
    {
        // 常规任务取完，去取长期任务
        m_status = 1;
        if(tasks_size == 0)
        {
            // 长期任务也取完
            getLongtermTasks(m_tasks);
            // 初始化状态
            TASK_MAP::iterator it;
            for(it = m_tasks.begin(); it != m_tasks.end(); ++it)
            {
                vector<string> status_set;
                status_set.push_back("0");
                status_set.push_back("0");
                status_set.push_back("-1");
                status_set.push_back(it->second.m_content);
                status_set.push_back(it->second.m_source);
                m_task_status.insert( pair<string, vector<string> >(it->second.m_workload_key, status_set) );
            }
        }
        srand(time(NULL));
        int j = rand() % m_tasks.size();
        TASK_MAP::iterator it = m_tasks.begin();
        int num = 0;
        for(; it != m_tasks.end(); ++it, ++num)
        {
            if( (it->second).m_is_assigned == 1 || m_forbidden_sources.find((it->second).m_source) != m_forbidden_sources.end() )
                continue;
            if(num == j)
            {
                task = it->second;
                //m_tasks.erase(it);
                m_tasks[it->first].m_is_assigned = 1;
            }
        }
    }
    return true;
}

string WorkloadMaster::assignTask(const string& source, int count)
{
    pthread_mutex_lock(&m_locker);
    if(count == 0)
    {
        Task task;
        if( !getTask(task) )
        {
            _ERROR("Get Task ERROR");
            pthread_mutex_unlock(&m_locker);
            return "";
        }
        pthread_mutex_unlock(&m_locker);
        return task.str();
    }
    else
    {
        vector<Task*> tasks;
        tasks.reserve(256);
        if( !getTasks(tasks, count) )
        {
            _ERROR("Get Task ERROR");
            pthread_mutex_unlock(&m_locker);
            return "";
        }
        // task列表序列化
        string res_str = "[";
        for(vector<Task*>::iterator it = tasks.begin(); it != tasks.end(); ++it)
        {
            res_str += (**it).str() + ",";
        }
        res_str.erase(res_str.end()-1);
        res_str += "]";
        pthread_mutex_unlock(&m_locker);
        return res_str;
    }
}

bool WorkloadMaster::updateUpdateTimes(const string& workload_key)
{
    ostringstream oss;
    oss << "UPDATE workload_longterm SET update_times = update_times + 1 WHERE workload_key = '" << workload_key << "'";
    return executeSQL(oss.str());
}

bool WorkloadMaster::updateSuccessTimes(const string& workload_key)
{
    // 更改状态，成功抓取
    m_task_status[workload_key][0] = "1";
    m_task_status[workload_key][1] = "1";
    
    // 插入mysql
    //ostringstream oss1, oss2;
    //oss1 << "UPDATE workload_longterm SET success_times = success_times + 1 WHERE workload_key = '" << workload_key << "'";
    //oss2 << "UPDATE workload_moniter_" << m_today.ToString(string("yyyyMMdd")) << " SET success_times = success_times +1, update_times = update_times + 1 WHERE workload_key = '" << workload_key << "'";
    //if(m_status == 1)
    //    executeSQL(oss2.str());
    //else
    //    executeSQL(oss1.str());
    return true;
}

bool WorkloadMaster::updateFailedTimes(const string& workload_key)
{
    // 更新状态，抓取一次，失败
    m_task_status[workload_key][0] = "1";
    //ostringstream oss;
    //oss << "UPDATE workload_moniter_" << m_today.ToString(string("yyyyMMdd")) << " SET error_times = error_times +1, update_times = update_times + 1 WHERE workload_key = '" << workload_key << "'";
    //string fail_sql = oss.str();
    //executeSQL(fail_sql);
    return true;
}

void WorkloadMaster::completeTask(const string& workload_key, int error)
{
    if(error == 0)
    {
        m_task_status[workload_key][2] = "0";
        updateSuccessTimes(workload_key);
    }
    else
    {
        ostringstream oss;
        oss << error;
        m_task_status[workload_key][2] = oss.str();
        updateFailedTimes(workload_key);
    }
}


bool WorkloadMaster::completeTask(const string& task_str)
{
    vector<Task*> tasks;
    if( !Task::parse(task_str, tasks) )
    {
        _ERROR("[IN completeTask: TASK PARSE ERROR!]");
        return false;
    }
    pthread_mutex_lock(&m_locker);
    for(vector<Task*>::iterator it = tasks.begin(); it != tasks.end(); ++it)
    {
        string workload_key = (*it)->m_workload_key;
        if(m_task_status.find( workload_key ) == m_task_status.end()){
            // 添加上个时间槽的任务
            vector<string> status;
            status.push_back("0");
            status.push_back("0");
            status.push_back("-1");
            status.push_back((*it)->m_content);
            status.push_back((*it)->m_source);
            m_task_status[workload_key] = status;
        }
        if(m_task_status[workload_key].size() != 5){
            // 验证解析是否正确
            _INFO("[IN completeTask: TASK %s SIZE IS NOT 5!]", workload_key.c_str());
            continue;
        }
        if((*it)->m_error == 0)
        {
            // 任务成功
            m_task_status[workload_key][2] = "0";
            updateSuccessTimes(workload_key);
        }
        else
        {
            // 任务失败
            ostringstream oss;
            oss << (*it)->m_error;
            _INFO("[zhangyang, in completeTask: error code is %d !]", (*it)->m_error);
            m_task_status[workload_key][2] = oss.str();
            updateFailedTimes(workload_key);
        }
    }
    pthread_mutex_unlock(&m_locker);
    return true;
}


void WorkloadMaster::addForbiddenSource(const string& source)
{
    if(m_forbidden_sources.find(source) == m_forbidden_sources.end())
    {
        m_forbidden_sources.insert(source);
    }
}

void WorkloadMaster::delForbiddenSource(const string& source)
{
    if(m_forbidden_sources.find(source) != m_forbidden_sources.end())
    {
        m_forbidden_sources.erase(source);
    }
}


void  WorkloadMaster::monitorTasks(int timeslot)
{
    int update_count = 0;
    int success_count = 0;

    STRING_MAP::iterator it = m_task_status.begin();

    // 更新抓取次数和成功次数
    for(; it != m_task_status.end(); ++it)
    {
        vector<string> status = it->second;
        update_count += atoi(status[0].c_str());
        success_count += atoi(status[1].c_str());
    }
    ostringstream oss1, oss2;
    oss1 << m_today.ToString(string("yyyyMMdd")) << "_" << timeslot;
    string patch = oss1.str();
    oss2 << "INSERT INTO workload_moniter (patch, timeslot, day, total, finish, success) VALUES ('" << patch << "','" << timeslot << "','" << m_today.ToString(string("yyyyMMdd")) << "','" << m_task_num << "','" << update_count << "','" << success_count << "')";
    string count_sql = oss2.str();
    executeSQL(count_sql);
    m_task_num = 0;

    // 分源更新错误信息
    Json::Value error_map;
    for(it = m_task_status.begin(); it != m_task_status.end(); ++it)
    {
        vector<string> status = it->second;
        string source = status[4];
        string error_type = status[2];
        if(error_type == "-1")
            continue;
        Json::Value source_error_map = error_map[source];
        source_error_map[error_type] = source_error_map.get(error_type, 0).asInt() + 1;
        error_map[source] = source_error_map;
        // 统计信息
        Json::Value stat_error_map = error_map["statistic"];
        stat_error_map[error_type] = stat_error_map.get(error_type, 0).asInt() + 1;
        error_map["statistic"] = stat_error_map;
        /*
        if(!source_error_map.isMember(error_type))
        {
           source_error_map[error_type]=0;
        }
        else{
           source_error_map[error_type] = source_error_map[error_type].asInt() + 1;
        }
        */
    }

    Json::FastWriter jfw;
    string error_info = jfw.write(error_map);
    ostringstream oss3;
    oss3 << "UPDATE workload_moniter SET errors = '" << error_info << "' where patch = '" << patch << "'";
    string error_sql = oss3.str();
    executeSQL(error_sql);
}
