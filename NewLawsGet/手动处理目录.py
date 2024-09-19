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
    title_url_all = content.find_all("div", class_="item")
    #
    titles_urls = {}
    for tag in title_url_all:
        title_a = tag.find('a', logfunc='文章点击', target='_blank', flink='true')
        if not title_a:
            continue
        title = title_a.get_text()
        url = title_a.get('href')

        # 创建字典来存储标题和URL
        titles_urls[title] = url
    return titles_urls


def not_need_tittle_del(titles_urls):
    li_need_dt = {}
    # 删除不需要的文章
    for title, url in titles_urls.items():
        status = elasticsearch_is_exist(title,'lar')
        status_s = elasticsearch_is_exist(title, 'chl')
        if status is True or status_s is True:
            li_need_dt[title] = url
    return li_need_dt


def calculate():
    # 读取html.text以获取页面所有文章的标题和url
    with open('html.text', 'r', encoding='utf-8') as file:
        h5 = str(file.read())
    h5 = BeautifulSoup(h5, 'html.parser')
    need_get_soup = h5.find("div", class_="accompanying-wrap")

    # 拿到所有标题与url的函数
    titles_urls = filter(need_get_soup)
    li_need_dt = not_need_tittle_del(titles_urls)

    # 创建DataFrame
    df = pd.DataFrame.from_dict(li_need_dt, orient='index', columns=['链接'])
    df.index.name = '标题'
    # 保存到Excel文件
    output_file = '手动获取的文章.xlsx'
    with pd.ExcelWriter(output_file) as writer:
        df.to_excel(writer, startrow=0, startcol=0)

    print(f"数据已成功保存到 {output_file}")


if __name__ == '__main__':
    calculate()
