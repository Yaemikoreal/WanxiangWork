import os
import pandas as pd
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from query.PublicFunction import load_config


es_client = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)

def check_article_exists(title, index_name='lar'):
    """
    检查 Elasticsearch 中是否存在给定标题的文章。

    参数:
    title (str): 文章标题。
    index_name (str): Elasticsearch 索引名称，默认为 'lar'。

    返回:
    bool: 如果文章不存在返回 True，否则返回 False。
    """
    query_body = {
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
        },
        "from": 0,
        "size": 10
    }
    response = es_client.search(index=index_name, body=query_body)
    if int(response['hits']['total']) == 0:
        print(f'{index_name} 不存在该文章!!  {title}')
        return None
    else:
        data_lt = response['hits']['hits']
        print(f'{index_name} 已经存在该文章!!  {title}，共有【{len(data_lt)}】个搜索结果。')
        return data_lt

def filter_unwanted_titles(titles_and_urls):
    """
    过滤掉不需要的文章标题。

    参数:
    titles_and_urls (list of dict): 包含标题和 URL 的字典列表。

    返回:
    list of dict: 过滤后的标题和 URL 字典列表。
    """
    filtered_titles_and_urls = []
    for item in titles_and_urls:
        data_lt = check_article_exists(item, 'chl')
        if data_lt:
            for it in data_lt:
                any_data_dt = it['_source']
                any_data_dt['法宝标题'] = item
                filtered_titles_and_urls.append(any_data_dt)
        else:
            filtered_titles_and_urls.append({'法宝标题': item})
        print("====="*20)
    return filtered_titles_and_urls


def calculate():
    data_df = pd.read_excel(r'E:\JXdata\Python\wan\NewLawsGet\附件\排查_法宝.xlsx')
    name_lt = data_df["标题"].tolist()
    new_name_lt = filter_unwanted_titles(name_lt)
    new_data_df = pd.DataFrame(new_name_lt)
    with pd.ExcelWriter('排查_81_结果_t1.xlsx') as writer:
        new_data_df.to_excel(writer, startrow=0, startcol=0, index=False)
    print(1)


if __name__ == '__main__':
    calculate()
