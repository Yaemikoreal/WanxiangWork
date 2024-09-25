import os
import re
import pandas as pd
from elasticsearch import Elasticsearch
import logging
from bs4 import BeautifulSoup
from query.PublicFunction import load_config

app_config = load_config(os.getenv('FLASK_ENV', 'test'))
ES_HOSTS = app_config.get('es_hosts')
ES_HTTP_AUTH = tuple(app_config.get('es_http_auth').split(':'))
logger = logging.getLogger('my_logger')
# 创建Elasticsearch客户端
es = Elasticsearch([ES_HOSTS], http_auth=ES_HTTP_AUTH)


def elasticsearch_is_exist(tittle, index_s='lar'):
    """

    :param tittle: 标题
    :param index_s: 'lar','chl'
    :return: 布尔值，判断是否有该文章
    """
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "标题": {
                                "query": tittle,
                                "slop": 0,
                                "zero_terms_query": "NONE",
                                "boost": 1.0
                            }
                        }
                    }
                ]
            }
        }, "from": 0,
        "size": 10
    }
    resp = es.search(index=index_s, body=body)  # 查询的库名
    if int(resp['hits']['total']) == 0:
        # print(f'{index_s} 不存在该文章!!  {tittle}')
        return True
    else:
        print(f'{index_s} 已经存在该文章!!  {tittle}')
        return False


def filter(content):
    """
       提取content中的所有标题和URL，并返回一个字典。

       Args:
       content (str): 包含HTML内容的字符串。

       Returns:
       dict: 包含标题作为键，URL作为值的字典。
       """
    need_get_soup = content.find("div", class_="accompanying-wrap")
    title_a_all = need_get_soup.find_all('a', logfunc='文章点击', target='_blank', flink='true')

    title_url_lt = []

    for tag in title_a_all:
        titles_urls = {}
        title = tag.get_text()
        url = tag.get('href')
        # print(f"标题: {title}")
        titles_urls['标题'] = title
        titles_urls['链接'] = url
        title_url_lt.append(titles_urls)

    return title_url_lt


def not_need_tittle_del(title_url_lt):
    new_title_url_lt = []
    # 删除不需要的文章
    for it in title_url_lt:
        li_need_dt = {}
        title = it.get('标题')
        # status = elasticsearch_is_exist(title, 'lar')
        status_s = elasticsearch_is_exist(title, 'chl')
        if status_s is True:
            li_need_dt['标题'] = title
            li_need_dt['链接'] = it.get('链接')
            new_title_url_lt.append(li_need_dt)
    return new_title_url_lt


def calculate():
    # 读取html.text以获取页面所有文章的标题和url
    with open('附件/html.text', 'r', encoding='utf-8') as file:
        h5 = str(file.read())
    h5 = BeautifulSoup(h5, 'html.parser')

    # 拿到所有标题与url的函数
    title_url_lt = filter(h5)
    new_title_url_lt = not_need_tittle_del(title_url_lt)

    # 创建DataFrame
    df = pd.DataFrame(new_title_url_lt)
    num_rows = df.shape[0]
    print(f"获取到 {num_rows}条需要Get的文章")
    df.index.name = '编号'
    # 保存到Excel文件
    output_file = '附件/手动获取的文章.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        df.to_excel(writer, startrow=0, startcol=0)

    print(f"数据已成功保存到 {output_file}")


if __name__ == '__main__':
    calculate()
