import time
import random

from NewLawsGet.GetTitleUrl import ES_CLIENT
from ProcessingMethod.LoggerSet import logger
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import requests
import re
import pandas as pd

headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "connection": "keep-alive",
    "content-length": "829",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "cookie": "_bl_uid=8tmqq2CO93Uw9bta8bjwdFIemC45; sensorsdata2015jssdkcross=%7B%22%24device_id%22%3A%22192e6e8033463-09f2438d266e14-4c657b58-1327104-192e6e803353a1%22%7D; chlOrderMemery=0; Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2206%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%220b1ef4c1-c209-ed11-b392-00155d3c0709%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1729214780,1729473999,1730683927,1731289225; HMACCOUNT=C1E3DEC5C46B85EE; cookieUUID=cookieUUID_1731289225446; pkulaw_v6_sessionid=xtjzxpfw532immjjnzk5laek; __tst_status=665643903#; referer=https://www.pkulaw.com/; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1731379511; xCloseNew=13",
    "host": "www.pkulaw.com",
    "origin": "https://www.pkulaw.com",
    "referer": "https://www.pkulaw.com/",
    "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "x-requested-with": "XMLHttpRequest"
}


def create_form_data(page_index):
    """
    创建用于发送请求的表单数据。
    适用于 法律法规
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
        'IsSearchProvision': 'False',
        'IsCustomSortSearch': 'False',
        'CustomSortExpression': '',
        'IsAdv': 'False',
        'ClassCodeKey': ',,,,,,',
        'Aggs.RelatedPrompted': '',
        'Aggs.EffectivenessDic': 'XE0304',
        'Aggs.SpecialType': '',
        'Aggs.IssueDepartment': '60322',
        'Aggs.TimelinessDic': '',
        'Aggs.Category': '',
        'Aggs.IssueDate': '',
        'GroupByIndex': '2',
        'OrderByIndex': '0',
        'ShowType': 'Default',
        'GroupValue': '',
        'TitleKeywords': '',
        'FullTextKeywords': '',
        'Pager.PageIndex': f'{page_index}',
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
    form_data = {
        'Menu': 'law',
        'Keywords': '',
        'SearchKeywordType': 'Title',
        'MatchType': 'Exact',
        'RangeType': 'Piece',
        'Library': 'chl',
        'ClassFlag': 'chl',
        'GroupLibraries': '',
        'QueryOnClick': 'False',
        'AfterSearch': 'False',
        'PreviousLib': 'chl',
        'pdfStr': '',
        'pdfTitle': '',
        'IsSynonymSearch': 'false',
        'RequestFrom': 'btnSearch',
        'LastLibForChangeColumn': 'chl',
        'IsSearchProvision': 'False',
        'IsCustomSortSearch': 'False',
        'CustomSortExpression': '',
        'IsAdv': 'False',
        'ClassCodeKey': ',,,,,,',
        'Aggs.RelatedPrompted': '',
        'Aggs.EffectivenessDic': '',
        'Aggs.SpecialType': '',
        'Aggs.IssueDepartment': '60322',
        'Aggs.TimelinessDic': '',
        'Aggs.Category': '',
        'Aggs.IssueDate': '',
        'GroupByIndex': '2',
        'OrderByIndex': '0',
        'ShowType': 'Default',
        'GroupValue': '',
        'TitleKeywords': '',
        'FullTextKeywords': '',
        'Pager.PageIndex': '1&1',
        'RecordShowType': 'List',
        'Pager.PageSize': '100',
        'QueryBase64Request': '',
        'VerifyCodeResult': '',
        'isEng': 'chinese',
        'OldPageIndex': '0',
        'newPageIndex': '',
        'IsShowListSummary': '',
        'X-Requested-With': 'XMLHttpRequest'
    }
    # form_data = {
    #     'Menu': 'law',
    #     'Keywords': '',
    #     'SearchKeywordType': 'Title',
    #     'MatchType': 'Exact',
    #     'RangeType': 'Piece',
    #     'Library': 'chl',
    #     'ClassFlag': 'chl',
    #     'GroupLibraries': '',
    #     'QueryOnClick': False,
    #     'AfterSearch': True,
    #     'PreviousLib': 'chl',
    #     'pdfStr': '',
    #     'pdfTitle': '',
    #     'IsSynonymSearch': False,
    #     'RequestFrom': 'btnSearch',
    #     'LastLibForChangeColumn': 'chl',
    #     'IsSearchProvision': 'False',
    #     'IsCustomSortSearch': 'False',
    #     'CustomSortExpression': '',
    #     'IsAdv': 'False',
    #     'ClassCodeKey': '',
    #     'Aggs.RelatedPrompted': '',
    #     'Aggs.EffectivenessDic': '',
    #     'Aggs.SpecialType': '',
    #     'Aggs.IssueDepartment': '',
    #     'Aggs.TimelinessDic': '',
    #     'Aggs.Category': '',
    #     'Aggs.IssueDate': '',
    #     'GroupByIndex': '2',
    #     'OrderByIndex': '',
    #     'ShowType': 'Default',
    #     'GroupValue': '',
    #     'TitleKeywords': '',
    #     'FullTextKeywords': '',
    #     'Pager.PageIndex': f'{page_index}',
    #     'RecordShowType': 'List',
    #     'Pager.PageSize': '100',
    #     'QueryBase64Request': 'eyJGaWVsZE5hbWUiOm51bGwsIlZhbHVlIjpudWxsLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjowLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoyLCJDaGlsZE5vZGVzIjpbeyJGaWVsZE5hbWUiOiJLZXl3b3JkU2VhcmNoVHJlZSIsIlZhbHVlIjpudWxsLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjowLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoxLCJDaGlsZE5vZGVzIjpbeyJGaWVsZE5hbWUiOiJLZXl3b3JkU2VhcmNoVHJlZSIsIlZhbHVlIjpudWxsLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjowLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoxLCJDaGlsZE5vZGVzIjpbeyJGaWVsZE5hbWUiOiJUaXRsZSIsIlZhbHVlIjoi5Lu35qC8566h55CGIiwiUnVsZVR5cGUiOjQsIk1hbnlWYWx1ZVNwbGl0IjoiXHUwMDAwIiwiV29yZE1hdGNoVHlwZSI6MSwiV29yZFJhdGUiOjAsIkNvbWJpbmF0aW9uVHlwZSI6MiwiQ2hpbGROb2RlcyI6W10sIkFuYWx5emVyIjoiaWtfbWF4X3dvcmQiLCJCb29zdCI6bnVsbCwiTWluaW11bV9zaG91bGRfbWF0Y2giOm51bGx9XSwiQW5hbHl6ZXIiOm51bGwsIkJvb3N0IjpudWxsLCJNaW5pbXVtX3Nob3VsZF9tYXRjaCI6bnVsbH0seyJGaWVsZE5hbWUiOiJOYXZDYXRhRGlyLlRpdGxlIiwiVmFsdWUiOiLku7fmoLznrqHnkIYiLCJSdWxlVHlwZSI6NCwiTWFueVZhbHVlU3BsaXQiOiJcdTAwMDAiLCJXb3JkTWF0Y2hUeXBlIjoxLCJXb3JkUmF0ZSI6MCwiQ29tYmluYXRpb25UeXBlIjoxLCJDaGlsZE5vZGVzIjpbXSwiQW5hbHl6ZXIiOiJpa19tYXhfd29yZCIsIkJvb3N0IjpudWxsLCJNaW5pbXVtX3Nob3VsZF9tYXRjaCI6bnVsbH1dLCJBbmFseXplciI6bnVsbCwiQm9vc3QiOm51bGwsIk1pbmltdW1fc2hvdWxkX21hdGNoIjpudWxsfV0sIkFuYWx5emVyIjpudWxsLCJCb29zdCI6bnVsbCwiTWluaW11bV9zaG91bGRfbWF0Y2giOm51bGx9',
    #     'VerifyCodeResult': '',
    #     'isEng': 'chinese',
    #     'OldPageIndex': previous_index,
    #     'newPageIndex': '',
    #     'IsShowListSummary': '',
    #     'X-Requested-With': 'XMLHttpRequest'
    # }

    return form_data


def make_request(page_index, params_data):
    """
    发送 POST 请求并返回响应文本。

    参数:
    page_index (int): 当前页面页数。
    返回:
    str: 响应文本。
    """
    url = 'https://www.pkulaw.com/law/search/RecordSearch'
    proxies = {
        'http': 'http://42.84.164.195:21979',
        'https': 'https://42.84.164.195:21979'
    }
    try_num = 3
    while try_num > 0:
        try:
            time.sleep(random.uniform(4, 5))
            ture_headers = headers
            response = requests.post(url, data=params_data, verify=False, headers=ture_headers)
            logger.info(f'连接状态<{response.status_code}>')
            if "<script>var _0x49" in response.text:
                try_num -= 1
                logger.info(f"重试,剩余重试次数:{try_num}")
            else:
                return response.text
        except Exception as e:
            logger.error(f'Exception occurred: {e}')


def other_msg_calculate(links_other_text):
    shixiao, xiaoli, bumen = None, None, None
    for link in links_other_text:
        text_msg = link.get_text()
        if any(keyword in text_msg for keyword in ['有效', '失效', '修改']):
            shixiao = text_msg
        if any(keyword in text_msg for keyword in ['文件', '法规', '规章', '批复']):
            xiaoli = text_msg
        if any(keyword in text_msg for keyword in ['人民', '政府', '委会', '局', '厅', '法院','其他']):
            bumen = text_msg
    return shixiao, xiaoli, bumen

def screening_date(links_text):
    fb_date, ss_date = None,None
    for link in links_text:
        dt_num = link.get_text()
        if "公布" in dt_num:
            fb_date = dt_num.replace('公布', '')
        if '施行' in dt_num:
            ss_date = dt_num.replace('施行', '')
    return fb_date, ss_date
def extract_titles_and_urls(content):
    """
    从网页内容中提取标题和 URL。适用于法律法规

    参数:
    content (str): 网页内容。

    返回:
    tuple: 包含状态 ('end' 或 'continue') 和标题与 URL 字典的元组。
    """
    count_num = 0
    titles_and_urls = []
    soup = BeautifulSoup(content, 'html.parser')
    container = soup.find("div", class_="accompanying-wrap")
    if not container:
        return
    # links = container.find_all('a', attrs={'logfunc': '文章点击', 'target': '_blank', 'flink': 'true'})
    msg_links = container.find_all('div', attrs={'class': 'item'})
    for it in msg_links:
        count_num += 1
        print(count_num)
        link_any = it.find('a', attrs={'logfunc': '文章点击', 'target': '_blank', 'flink': 'true'})
        if not link_any:
            link_any = it.find('a', attrs={'target': '_blank', 'flink': 'true'})
        links_text = it.find_all('span', attrs={'class': 'text'})
        links_other_text = it.find_all('a', attrs={'target': '_blank'}, href=True)
        shixiao, xiaoli, bumen = other_msg_calculate(links_other_text)

        if link_any or links_text:
            fb_date, ss_date = screening_date(links_text)
            biaoti = link_any.get_text().replace("\n", '')
            # 去除首尾的空格
            biaoti = biaoti.strip()
            # 将多个连续的空格替换为单个空格
            biaoti = ' '.join(biaoti.split())
            data_dt = {
                '标题': biaoti,
                '链接': link_any.get('href'),
                '发文字号': screening_document_number(links_text),
                '发布日期': fb_date,
                '实施日期': ss_date,
                '时效性': shixiao,
                '效力级别': xiaoli,
                '发布部门': bumen
            }
            titles_and_urls.append(data_dt)
    # titles_and_urls = [{'标题': link.get_text(), '链接': link.get('href')} for link in links]
    return titles_and_urls

def screening_document_number(links_text):
    for link in links_text:
        dt_num = link.get_text()
        if "号" in dt_num:
            return dt_num
    return None

def check_elasticsearch_existence(title, index):
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
    response = ES_CLIENT.search(index=index, body=query_body)
    if int(response['hits']['total']) == 0:
        # logger.info(f'文章不存在: {title}')
        return True
    else:
        # logger.info(f'存在文章: {title}')
        return False


def get_title_url():
    # 页数
    page_index = 0

    needed_content_lt = []
    last_content = None
    while True:
        logger.info(f"当前获取{page_index + 1}页!!!")
        params_data = create_form_data(page_index)

        # 发送 POST 请求并返回响应文本
        content = make_request(page_index, params_data=params_data)
        if content == last_content:
            logger.info("该页内容和上一页一样！！！")
            page_index += 1
            if page_index > 25:
                logger.info("获取完毕!!!")
                return needed_content_lt
            continue
        # 从网页内容中提取标题和 URL
        titles_and_urls = extract_titles_and_urls(content)
        if not titles_and_urls:
            continue
        if len(titles_and_urls) > 0:
            logger.info(f"从第 {page_index + 1} 页获取到了 {len(titles_and_urls)} 篇文章!!!")
            for it in titles_and_urls:
                logger.info(f"添加标题:{it.get('标题')}  {it.get('链接')}")
                needed_content = {
                    '标题': it.get('标题'),
                    '链接': it.get('链接'),
                    '发文字号': it.get('发文字号'),
                    '发布日期': it.get('发布日期'),
                    '实施日期': it.get('实施日期'),
                    '时效性': it.get('时效性'),
                    '效力级别': it.get('效力级别'),
                    '发布部门': it.get('发布部门')
                }
                needed_content_lt.append(needed_content)
            if page_index > 25:
                logger.info("获取完毕!!!")
                return needed_content_lt
        else:
            logger.info("获取失败!!!(或已经获取完毕)")
            return needed_content_lt
        last_content = content
        page_index += 1


def save_to_excel(dataframe, filename):
    """
    保存DataFrame到Excel文件
    """
    with pd.ExcelWriter(filename) as writer:
        dataframe.to_excel(writer, startrow=0, startcol=0)
    logger.info(f"{filename} 写入完毕！！！")


def calculate(choose=True):
    # 收录内容
    needed_content_lt = get_title_url()

    if needed_content_lt:
        df = pd.DataFrame(needed_content_lt)
        df.index.name = '标题'
        filename = '附件/排查_行政许可批复_正.xlsx'
        save_to_excel(df, filename)
        return True
    return False


if __name__ == '__main__':
    calculate()
