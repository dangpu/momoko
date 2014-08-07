#!/usr/bin/env python
#coding=UTF8
'''
    @author: devin
    @time: 2014-02-22
    @desc:
        保存slave的相关信息
'''
import jsonlib

class SlaveInfo:
    def __init__(self):
        self.id = None              # id
        self.name = None            # slave名称
        self.server = None          # 所在机器的IP地址
        self.path = None            # 所在机器路径
        self.server_ip = None       # 提供服务的地址，包括端口号，提供给real_time_request使用
        self.start_time = None      # 开始运行时间
        self.thread_num = 0         # 运行的线程数目
        self.process_task_num = 0   # 总共处理task个数
        self.error_task_num = 0     # 出错task个数
        self.type = None            # slave类型
        self.last_heartbeat = None  # 最后一次上报心跳信息时间
        self.status = 0             # 状态, 1表示正常，-1表示丢失连接
        self.request_task_num = 0   # 实时请求次数
        self.recv_real_time_request = False # 是否接收实时请求
    
    def __str__(self):
        return jsonlib.write(self.__dict__)
