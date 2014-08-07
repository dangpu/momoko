#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @time: 2014-02-23
    @desc:
        
'''
from crawler.controller.slave import Slave
from crawler.worker import Workers
from workload import ControllerWorkload
from common.task import RequestTask
from common.logger import logger
from common.common import set_proxy_client
from util import http_client
import time
import jsonlib
import threading

workload = None
info = None
parsers = {}
SINGLE_REQUEST_TIMEOUT = 15
MULTI_REQUEST_TIMEOUT = 60
PARSER_ERROR = 11
SLAVE_ERROR = 41
TYPE_DICT = {"singleTask":4101,"parallelTask":4100}
parsers_dict = {"wego":"wegoFlight","ctrip":"ctripFlight","elong":"elongFlight",\
        "ryanair":"ryanairFlight","vueling":"vuelingFlight","jijitong":"jijitongFlight",\
        "feifan":"feifanFlight","youzhan":"youzhanHotel","qunar":"qunarHotel"}

class RequestSingle(object):
    def __init__(self,task):
        self.__task_str = task
        self.__result = -1
        
    def start(self):

        task = self.__task_str

        #task_str是字符串
        #task = jsonlib.read(task_str)
        try:
            source = task.split('|')[-1].strip().split('::')[0].strip()
        except Exception,e:
            logger.error('Source Error:' + str(e))
            source = None

        if parsers_dict.has_key(source):
            parser_name = parsers_dict[source]

            parser = parsers[parser_name]

            for i in range(2):
                logger.info(type(task).__name__)
                self.__result = parser.request(task)
                if self.__result != -1:
                    break

        return self.__result

    def stop(self):
        pass
    
    def get_result(self):

        return self.__result
            

class RequestThread(object):
    def __init__(self,tasks):
        self.__task_str = tasks
        self.__taskstatus = { }
        self.__threads = []

    def start(self):

        if len(self.__task_str.strip()) == 0:
            return self.__taskstatus

        #tasks为json格式
        tasks = jsonlib.read(self.__task_str)

        for k,v in tasks.items():
            logger.error("RequestThread::start k = %s v = %s" %(k, v))
            self.__taskstatus[k] = -1
            t = threading.Thread(target=self.single_task,args = (k,v))
            self.__threads.append(t)

        for thread in self.__threads:
            thread.start()

        for thread in self.__threads:
            thread.join(MULTI_REQUEST_TIMEOUT)

    def single_task(self,task_key,task):
        
        if task != None:
            try:
                source = task.split('|')[-1].strip().split('::')[0].strip()
            except Exception,e:
                logger.error('Source Error:' +  str(e))
                source = None

            if parsers_dict.has_key(source):
                parser_name = parsers_dict[source]

                parser = parsers[parser_name]

                for i in range(2):

                    result = parser.request(task)
                    if result != -1:
                        break

                
                self.__taskstatus[task_key] = result


    def get_result(self):

        import json
        logger.error("RequestThread::get_result relt = %s" % json.dumps(self.__taskstatus))
        return json.dumps(self.__taskstatus)


def load_parsers(config):
    '''
        根据配置文件加载所有的parsers
    '''
    import sys
    import new
    parsers = {}
    strs = config.get("slave", "parsers").strip().split(" ")
    for name in strs:
        name = name.strip()
        if len(name) == 0:
            continue
        file_path = config.get(name, "file_path")
        class_name = config.get(name, "class_name")
        sys.path.append(file_path)
        mod = __import__(name)
        clazz= getattr(mod, class_name)
        parser = new.instance(clazz)
        
        source = config.get(name, "source")
        source = source.strip()
        parsers[source] = parser
    return parsers

def work():
    '''
        
    '''
    task = workload.assign_workload()
    if task == None:
        time.sleep(1)
        return
    
    # 根据source选指定的parser
    if task.source not in parsers:
        logger.error("no parser for the source %s" % task.source)
        time.sleep(1)
        error = PARSER_ERROR
        return error
    
    info.process_task_num += 1
    
    #logger.info("begin to parse %s" % task.source)
    parser = parsers[task.source]
    
    error = 0
    try:
	#logger.info("start parse %s" % task.str())
	error = parser.parse(task)
	#logger.info("complete parse %s" % task.str())
    except Exception, e:
        logger.error("Parser Exception: task_id: %s  %s" %(task.id, str(e)))
        error = SLAVE_ERROR
    
    if error:
        info.error_task_num += 1

    workload.complete_workload(task, error)


def request(params):

    stime = int(time.time() * 1000)

    info.request_task_num += 1

    try:
        taskcontent = params.get("query").encode('utf-8')
        tasktype = params.get("type")
        #logger.info(q)
        #logger.info(str(type))
    except Exception,e:
        logger.error(str(e))
        return None

    if int(tasktype) == TYPE_DICT["singleTask"]:

        requestTask = RequestSingle(taskcontent)

        resp =  requestTask.start()

        #try:
            #resp = requestTask.get_result()
        #except Exception, e:
            #logger.error(str(e))
            #return -1
        
        etime = int(time.time() * 1000)
        during = etime - stime
        logger.info('%d content(s), costing %d s'%(len(taskcontent),during/1000))
        return resp

    elif int(tasktype) == TYPE_DICT["parallelTask"]:

        requestTask = RequestThread(taskcontent)

        requestTask.start()

        try:
            resp = requestTask.get_result()
        except Exception, e:
            logger.error(str(e))
            return {}
        etime = int(time.time() * 1000)
        during = etime - stime
        logger.info('%d content(s), costing %d s'%(len(taskcontent),during/1000))

        return resp

    else:
        return None


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s config_file_path" % sys.argv[0]
        sys.exit()
    
    # 读取配置文件
    import ConfigParser
    config = ConfigParser.ConfigParser()
    config.read(sys.argv[1])
    
    # set proxy client
    proxy_client = http_client.HttpClientPool(config.get("proxy", "host"))
    set_proxy_client(proxy_client)
    
    host, port = config.get("slave", "host"), config.getint("slave", "port")
    master_host = config.get("master", "host")
    
    # 如果有配置sources，只抓取sources指定的task
    sources = []
    if config.has_option("slave", "sources") and len(config.get("slave", "sources").strip()) > 0:
        sources = config.get("slave", "sources").strip().split(" ")

    workload = ControllerWorkload(master_host, sources)
    
    parsers = load_parsers(config)
    
    workers = Workers(work, config.getint("slave", "thread_num"))
    slave = Slave(host, port, master_host, workers, True)
    
    slave.info.name = config.get("slave", "name")
    slave.register("/request", request)
    
    info = slave.info
    
    slave.run()

