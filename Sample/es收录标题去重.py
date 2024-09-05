import re
from elasticsearch import Elasticsearch
import pyodbc


def sql_data():
    conn = pyodbc.connect('DRIVER={SQL Server};'
                        'SERVER=47.97.3.24,14333;'
                        'DATABASE=自收录数据;'
                        'UID=saa;'
                        'PWD=1+2-3..*Qwe!@#')
    cursor = conn.cursor()
    select_query ="SELECT 法规标题 FROM [dbo].[专项补充收录] WHERE [唯一标志] LIKE '%hb17%'"
    cursor.execute(select_query)
    rows = cursor.fetchall()
    return rows

es = Elasticsearch(
    # ['47.97.3.24:59200'],
    ['10.0.0.1:8041'],
    # 认证信息
    # http_auth=('elastic', 'Cdxb1998123!@#cs')
    http_auth=('elastic', 'Cdxb1998123!@#')
)
# http://47.97.3.24:59200/lar/_mapping
# print(es.ping())
# print(es.cat.indices())

# ccs = re.compile(r'\(|\)|（|）|《|》| ')
ccs = re.compile('((?=[\x21-\x7e]+)[^A-Za-z0-9])| |》|《|·|！|￥|…|（|）|—|\r|\t|\n')

def esquc_lar(title):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "标题": {
                                "query": title,
                                "slop": 0,
                                "zero_terms_query": "NONE",
                                "boost": 1.0
                            }
                        }
                    }
                ]
            }
        }
        ,"from": 0, "size": 10,
        "stored_fields": ["全文"]
    }
    res = es.search(index='lar', body=body)
    list=res['hits']['hits']
    if list !=[]:
        content=list[0]['fields']['全文']
        content1 = content[0].replace("'", '"')
        return content1
    else:
        content=''
        return content

def esquc_chl(title):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "标题": {
                                "query": title,
                                "slop": 0,
                                "zero_terms_query": "NONE",
                                "boost": 1.0
                            }
                        }
                    }
                ]
            }
        }
        ,"from": 0, "size": 10,
        "stored_fields": ["全文"]
    }
    res = es.search(index='chl', body=body)
    list=res['hits']['hits']
    if list !=[]:
        content=list[0]['fields']['全文']
        content1 = content[0].replace("'", '"')
        return content1
    else:
        content=''
        return content

def lar_esquc(title):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "标题": {
                                "query": title,
                                "slop": 0,
                                "zero_terms_query": "NONE",
                                "boost": 1.0
                            }
                        }
                    }
                ]
            }
        }
    }
    resp = es.search(index='lar', body=body)
    list = resp['hits']['hits']
    if list !=[]:
        for zd in list:
            title=zd['_source']['标题']
            return "法器地方法规有这条数据："+title
    else:
        return

def chl_esquc(title):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "标题": {
                                "query": title,
                                "slop": 0,
                                "zero_terms_query": "NONE",
                                "boost": 1.0
                            }
                        }
                    }
                ]
            }
        }
    }
    resp = es.search(index='chl', body=body)
    list = resp['hits']['hits']
    if list !=[]:
        for zd in list:
            title=zd['_source']['标题']
            return "法器法律法规库有这条数据："+title
    else:
        return

# print(esquc_lar('辽宁省人民代表大会及其常务委员会立法条例(2023修正)'))
