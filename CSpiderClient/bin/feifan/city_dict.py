#!/usr/bin/env python
#coding=UTF8

'''
    生成静态iatacode与城市中文名、城市拼音的map
'''

import db
import json

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

wfile = open('city_dict','w')

sql = "SELECT * FROM airport WHERE 1"

results = db.QueryBySQL(sql)

dict1 = { }
dict2 = { }
dict3 = { }

for result in results:
    dict1[result["iatacode"].encode('utf-8')] = result["city"].encode('utf-8')
    dict2[result["iatacode"].encode('utf-8')] = result["city_cn_name"].encode('utf-8')
    dict3[result["iatacode"].encode('utf-8')] = result["city_pinyin"].encode('utf-8')


wfile.write(json.dumps(dict1) + '\n' + json.dumps(dict2) + '\n' + json.dumps(dict3))

wfile.close()
