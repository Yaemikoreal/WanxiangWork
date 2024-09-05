import re
from elasticsearch import Elasticsearch
from botpy import logging

_log = logging.get_logger()
"""
本方法用于，拿到了标题先判断系统里有没有，没有的话，才进行全文以及其他字段收录
"""

# es = Elasticsearch(['http://10.0.0.1:8041'], basic_auth=('elastic', 'Cdxb1998123!@#'))
es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)
ddd = '重庆'


def select(list_name, titl, chean_text, quer, fm):
    resp = es.search(index=['lar', 'chl'], body=quer)
    hits_total = resp["hits"]["hits"]
    z = 0
    for hits in hits_total:
        z += 1
        # print(hits)
        title = hits['_source']['标题']
        title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
        titl = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', titl)
        try:
            wenhao = hits['_source']['发文字号']
        except:
            wenhao = 'aaaaaaa'
        try:
            libb = hits['_source']['lib']
        except:
            libb = ''
        if wenhao:
            wenhao = wenhao
        else:
            wenhao = 'aaaaaaa'
        wenhao = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', wenhao)
        # print(chean_text,title)
        try:
            jigou = hits['_source']['发布部门']
        except:
            jigou = ''
        if jigou == '':
            if list_name == '标题':
                a = (titl in title or title in titl)
            else:
                a = (
                        chean_text in wenhao or wenhao in chean_text or titl in title or title in titl or 'chl' in libb)
        else:
            if list_name == '标题':
                a = (titl in title or title in titl) and (fm in jigou or 'chl' in libb)
            else:
                a = (chean_text in wenhao or wenhao in chean_text or titl in title or title in titl) and (
                        fm in jigou or 'chl' in libb)
        if a:
            return True
        elif z <= len(hits_total) and a:
            return True
        elif z < len(hits_total) and not a:
            pass
        else:
            return False


def check_existence(input_data, title, column, quer, fm):
    '''
    该函数用于判断新收录文件标题是否存在法器当中
    :param input_data: 新收录文件标题
    '''
    title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
    if '转发' not in title:
        chean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  #.split('关于')[-1]
    else:
        chean_text = title
    a = select(column, title, chean_text, quer, fm)
    if a:
        # print(rf'{input_data}存在于法器中')
        return True
    else:
        # print(rf'{input_data}不存在于法器中')
        return False


def lar_esquc(title, column, issued_date=None):
    if '转发' not in title:
        clean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  #.split('关于')[-1]
    else:
        clean_text = title
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            column: {
                                "query": clean_text,
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
    list_a = resp['hits']['hits']
    if list_a:
        for it in list_a:
            title_real = it['_source'].get('标题')
            issued_date_real = it['_source'].get('发布日期')
            # 当标题等于传入标题的同时，如果有传入发布日期，那么就判断发布日期是否一致
            if title == title_real:
                if issued_date:
                    if issued_date_real == issued_date:
                        return True
                else:
                    return True
    else:
        return False



def query(list_name, ddd1, ddd2):
    query1 = {
        "query": {"bool": {
            "must": [{"match_phrase": {list_name: ddd1}},
                     {"match_phrase": {list_name: ddd2}}]}}}
    query2 = {"query": {"match": {list_name: ddd2}}}
    return [query1, query2]


def main_panduan(title_a, fm='831', ddd='重庆' ,issued_number=None, issued_date=None):
    """
    判断es数据库中是否已经有这个文章内容
    :param ddd:
    :param title_a:  标题
    :param fm: 文章来源地区编号（例如重庆市：831）
    :param issued_number: 发文字号
    :return:
    """
    chatitle = title_a
    query1 = query('标题', ddd, chatitle)[0]
    a = check_existence(title_a, title_a, '标题', query1, fm)
    if issued_number:
        query2 = query('发文字号', ddd, issued_number)[1]
        b = check_existence(issued_number, issued_number, '发文字号', query2, fm)
        if (lar_esquc(title_a, '标题', issued_date) or a) and title_a[-3:] != '...':
            return True
        else:
            if (lar_esquc(issued_number, '发文字号', issued_date) or b) and len(issued_number.strip()) > 2:
                return True
        return False
    else:
        a = check_existence(title_a, title_a, '标题', query1, fm)
        if (lar_esquc(title_a, '标题', issued_date) or a) and title_a[-3:] != '...':
            return True
        return False



if __name__ == '__main__':
    title = '重庆市司法重庆市档案局关于印发《司法鉴定业务档案管理暂行办法》的通知'
    issued_number = '渝司办〔2006〕90号'
    print(main_panduan(title, issued_number))
    # # 测试连接
    # info = es.info()
    # print(info)
