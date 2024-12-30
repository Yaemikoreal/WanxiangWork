# -*- coding: utf-8 -*-
import csv
import re

from pyquery.pyquery import PyQuery as pq
# -*- coding: utf-8 -*-
import time
# from mysql_base import MysqlBase
from elasticsearch import Elasticsearch
import re
import pandas as pd

es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)
for year in range(1992, 1995):
    print(year)
    resalu = {'唯一标志': [], '标题': [], '发文字号': [], '发布日期': [], '实施日期': [], '时效性': [], '发布部门': [], '效力级别': [], '部门': []}
    # for fff in range(0, 1000000, 10000):
    hits=[1]
    fff=0
    while len(hits) <500000 and hits==[1]:
        print(fff)
        body = {"query": {"bool": {
            "must": [{
                "range": {
                    "发布日期": {
                        "gte": f"{year}.01.01",
                        "lte": f"{year}.12.31"
                    }}}]}}, "from": fff, "size": 500000,
            "_source": []}
        fff+=500000
        res = es.search(index="lar", body=body)
        hits = res['hits']['hits']
        for hit in hits:
            try:
                Issued_Number = str(hit['_source']['发文字号'])
            except:
                Issued_Number = ''
            try:
                departments = str(hit['_source']['发布部门']).replace("', '", ';').replace("['", '').replace("']", '')
            except:
                departments = ''
            try:
                Release_date = str(hit['_source']['发布日期'])
            except:
                Release_date = ''
            try:
                Implementation_date = str(hit['_source']['实施日期'])
            except:
                Implementation_date = ''
            try:
                effectiveness_level = str(hit['_source']['效力级别']).replace("', '", ';').replace("['", '').replace("']", '')
            except:
                effectiveness_level = ''
            try:
                Timeliness = str(hit['_source']['时效性'])
            except:
                Timeliness = ''
            try:
                departments = str(hit['_source']['发布部门']).replace("', '", ';').replace("['", '').replace("']", '')
            except:
                departments = ''
            try:
                departments1 =re.findall(';(\d{3});', str(hit['_source']['发布部门']).replace("', '", ';').replace("['", '').replace("']", ''))[0]
            except:departments1=''
            resalu['唯一标志'].append(hit['_id'])
            resalu['标题'].append(str(hit['_source']['标题']))
            resalu['发文字号'].append(Issued_Number)
            resalu['发布部门'].append(departments)
            resalu['发布日期'].append(Release_date)
            resalu['实施日期'].append(Implementation_date)
            resalu['时效性'].append(Timeliness)
            resalu['效力级别'].append(effectiveness_level)
            resalu['部门'].append(departments1)
            # print(hit)
    result_df = pd.DataFrame(resalu)
    result_df.to_excel(rf'E:\JXdata\Python\wan\测试\全部数据\全部数据{year}.xlsx', index=False)