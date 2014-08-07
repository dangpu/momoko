#!/usr/bin/env python
#coding=UTF-8
'''
    Created on 2014-03-08
    @author: devin
    @desc:
        数据访问
'''
import sys
import MySQLdb
from MySQLdb.cursors import DictCursor
import datetime
from logger import logger

# MySQL 连接信息
MYSQL_HOST = '115.29.78.222'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PWD = 'miaoji@2014!'
MYSQL_DB = 'crawl'

def GetConnection():
    conn = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PWD, \
                           db=MYSQL_DB, charset="utf8")
    return conn

def ExecuteSQL(sql, args = None):
    '''
        执行SQL语句, 正常执行返回影响的行数，出错返回Flase 
    '''
    ret = 0
    try:
        conn = GetConnection()
        cur = conn.cursor()

        ret = cur.execute(sql, args)
        conn.commit()
    except MySQLdb.Error, e:
        logger.error("ExecuteSQL error: %s" %str(e))
        return False
    finally:
        cur.close()
        conn.close()

    return ret

def ExecuteSQLs(sql, args = None):
    '''
        执行多条SQL语句, 正常执行返回影响的行数，出错返回Flase 
    '''
    ret = 0
    try:
        conn = GetConnection()
        cur = conn.cursor()

        ret = cur.executemany(sql, args)
        conn.commit()
    except MySQLdb.Error, e:
        logger.error("ExecuteSQL error: %s" %str(e))
        return False
    finally:
        cur.close()
        conn.close()

    return ret

def QueryBySQL(sql, args = None, size = None):
    '''
        通过sql查询数据库，正常返回查询结果，否则返回None
    '''
    results = []
    try:
        conn = GetConnection()
        cur = conn.cursor(cursorclass = DictCursor)
        
        cur.execute(sql, args)
        rs = cur.fetchall()
        for row in rs : 
            results.append(row)
    except MySQLdb.Error, e:
        logger.error("QueryBySQL error: %s" %str(e))
        return None
    finally:
        cur.close()
        conn.close()

    return results
