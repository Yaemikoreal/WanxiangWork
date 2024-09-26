import time
import random
from elasticsearch import Elasticsearch
import requests
import re
import pandas as pd

"""
该方法用于自动获取法宝新法速递标题和url信息

注意:运行该方法前，先启动NewInterface脚本！！！

输出内容存在于:附件/chl.xlsx中.
"""

# 代理配置
PROXY = '127.0.0.1:1080'
PROXIES = {
    'http': f'socks5://{PROXY}',
    'https': f'socks5://{PROXY}'
}

# Elasticsearch 配置
ES_CLIENT = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


def check_elasticsearch_existence(title):
    """
    检查 Elasticsearch 中是否存在给定标题的文章。

    参数:
    title (str): 文章标题。

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
    response = ES_CLIENT.search(index='chl', body=query_body)
    if int(response['hits']['total']) == 0:
        print(f'文章不存在: {title}')
        return True
    else:
        print(f'存在文章: {title}')
        return False


def create_form_data(page_index):
    """
    创建用于发送请求的表单数据。

    参数:
    page_index (int): 当前页面索引。

    返回:
    dict: 表单数据字典。
    """
    previous_index = page_index - 1
    if previous_index < 0:
        previous_index = 0
    form_data = {
        'Menu': 'law',
        'Keywords': '',
        'SearchKeywordType': 'Title',
        'MatchType': 'Exact',
        'RangeType': 'Piece',
        'Library': 'chl',
        'ClassFlag': 'chl',
        'GroupLibraries': '',
        'QueryOnClick': False,
        'AfterSearch': False,
        'PreviousLib': 'chl',
        'pdfStr': '',
        'pdfTitle': '',
        'IsSynonymSearch': False,
        'RequestFrom': 'btnSearch',
        'LastLibForChangeColumn': 'chl',
        'IsAdv': False,
        'ClassCodeKey': ',,,,,,',
        'Aggs.RelatedPrompted': '01',
        'Aggs.EffectivenessDic': '',
        'Aggs.SpecialType': '',
        'Aggs.IssueDepartment': '',
        'Aggs.TimelinessDic': '',
        'Aggs.Category': '',
        'Aggs.IssueDate': '',
        'GroupByIndex': '2',
        'OrderByIndex': '0',
        'ShowType': 'Default',
        'GroupValue': '',
        'TitleKeywords': '',
        'FullTextKeywords': '',
        'Pager.PageIndex': page_index,
        'RecordShowType': 'List',
        'Pager.PageSize': '100',
        'QueryBase64Request': '',
        'VerifyCodeResult': '',
        'isEng': 'chinese',
        'OldPageIndex': previous_index,
        'newPageIndex': '',
        'IsShowListSummary': '',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return form_data


def make_request(page_index):
    """
    发送 POST 请求并返回响应文本。

    参数:
    page_index (int): 当前页面索引。

    返回:
    str: 响应文本。
    """
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Referer': 'https://jjll.tytyxdy.com/https/44696469646131313237446964696461bd6feb2613c3be1bcd4ca96fd868/law',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    url = 'https://www.pkulaw.com/law/search/RecordSearch'
    time.sleep(random.uniform(2, 4))

    try:
        response = requests.post(url, data=create_form_data(page_index), verify=False, headers=headers)
        print(f'连接状态<{response.status_code}>')
        return response.text
    except Exception as e:
        print(f'Exception occurred: {e}')
        return make_request(page_index)


def extract_titles_and_urls(content):
    """
    从网页内容中提取标题和 URL。

    参数:
    content (str): 网页内容。

    返回:
    tuple: 包含状态 ('end' 或 'continue') 和标题与 URL 字典的元组。
    """
    pattern = re.compile(
        r'<a bdclick logfunc="文章点击" logplace="右侧列表" logplate="列表" logother=".*?" target="_blank" flink="true" href="(?P<url>.*?)">(?P<title>.*?)</a>',
        re.S)
    matches = pattern.finditer(content)
    titles_and_urls = {match.group('title'): match.group('url') for match in matches}

    if not titles_and_urls:
        print('获取标题与URL数据内容为空！！！')
        return 'end', {}

    print(titles_and_urls)
    return 'continue', titles_and_urls


def remove_unwanted_titles(titles_and_urls):
    """
    移除不需要的文章标题。

    参数:
    titles_and_urls (dict): 标题与 URL 的字典。

    返回:
    dict: 过滤后的标题与 URL 字典。
    """
    unwanted_keywords = [
        '免职通知', '免职的通知', '放假通知', '任职通知', '任职的通知', '比赛通知', '放假的通知',
        '同志退休', '同志任免职的通知', '同志晋升职级的通知', '同志免职', '同志任职的通知',
        '同志工作安排的通知', '年春节放假的通知', '赛的通知', '同志退休', '同志职务调整的通知',
        '同志任职的决定', '职务任免的通知', '工作职务的通知', '同志工作调整的通知', '邀请函',
        '晋升通知', '晋升的通知', '晋升职级的通知', '退休的通知', '任用的通知', '同志职务变动的通知',
        '任免职务的通知', '套转职级的通知', '公开赛', '任职资格的批复', '击剑'
    ]
    filtered_titles_and_urls = {}

    for title, url in titles_and_urls.items():
        if not any(keyword in title for keyword in unwanted_keywords):
            filtered_titles_and_urls[title] = url

    print(f'一共获取到 {len(filtered_titles_and_urls)} 篇有效文章!!!')
    return filtered_titles_and_urls


# 主程序
def calculate():
    # 页数
    page_index = 0
    # 收录内容
    needed_content = {}
    while True:
        # 发送 POST 请求并返回响应文本
        content = make_request(page_index)

        # 从网页内容中提取标题和 URL
        state, titles_and_urls = extract_titles_and_urls(content)

        if state == 'continue':
            print(f"正在获取第 {page_index + 1} 页内容!!!")
            for title, url in titles_and_urls.items():
                # 检查 Elasticsearch 中是否存在给定标题的文章。
                if check_elasticsearch_existence(title):
                    needed_content[title] = url
        else:
            print("获取失败!!!(或已经获取完毕)")
            break
        page_index += 1

    # 移除不需要的文章标题
    final_content = remove_unwanted_titles(needed_content)

    if final_content:
        df = pd.DataFrame.from_dict(final_content, orient='index', columns=['链接'])
        df.index.name = '标题'
        with pd.ExcelWriter('附件/chl.xlsx') as writer:
            df.to_excel(writer, startrow=0, startcol=0)
        print("写入完毕！！！")


if __name__ == '__main__':
    main()
