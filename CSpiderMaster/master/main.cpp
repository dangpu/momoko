#include <string>
#include <iostream>
#include "data.hpp"
#include "master.hpp"
#include "workload.hpp"
using namespace std;

int main()
{
    // test SlaveInfo::str(), Task::str()
    SlaveInfo si;
    Task task;
    cout << si.str();
    cout << task.str();
    cout << "................................" << "SlaveInfo::str() done!"  << ".............................." << endl;
    cout << "................................" << "Task::str() done!"  << "..............................." << endl;

    ostringstream oss;
    oss << "[{'id':" << "'1'},{'error':0}]";
    vector<Task*> tasks;
    cout << oss.str() << endl;
    Task::parse(oss.str(), tasks);
    cout << tasks.size() << endl;

    // test SlaveInfo::parse(), Task::parse()
    //string tmp = task.str();
    //task.m_id = "5";
    //task.parse(tmp);
    //cout << task.m_id << endl;
    //si.parse(si.str());
    //cout << si.m_name << endl;
    cout << "................................" << "SlaveInfo::parse() done!"  << ".............................." << endl;
    cout << "................................" << "Task::parse() done!"  << "..............................." << endl;
    
    Master* master = Master::getInstance();
    // test Master::registerSlave
    cout << "slave id is : " << master->registerSlave("test_slave", "127.0.0.1", "/test", "127.0.0.1:8080", "-1", false) << endl;
    cout << "................................" << "Master::registerSlave() done!"  << "..............................." << endl;
    // test Master::heartbeat
    master->heartbeat("1", 10, 2, 2, 2);
    cout << "last heartbeat time is : " << master->m_slave_map["1"].m_last_heartbeat << endl;
    cout << "................................" << "Master::heartbeat() done!"  << "..............................." << endl;
    // test Master::getStatus
    cout << "slave 1 status is : " << master->getStatus("1");
    cout << "................................" << "Master::getStatus() done!"  << "..............................." << endl;

    cout << DateTime::Today().ToString(DateTimeFormatInfo::en_USInfo) << endl;
    cout << DateTime::Today().GetDayOfMonth() << endl;
    cout << DateTime::Today().ToString(string("yyyyMMdd")) << endl;


    // test workload
    TASK_MAP _tasks;
    WorkloadMaster* workload = WorkloadMaster::getInstance();
    workload->getLongtermTasks(_tasks);
    //workload->updateWorkload();
    //vector<Task> tasks;
    //workload->getTasks(tasks, 5);
    //cout << tasks[0].str() << endl;
    //cout << workload->assignTask("airberlin", 5) << endl;
    return 0;
}
