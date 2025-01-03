# https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%2C%2C%2C0%3B60322%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0%2C0%3B0&lib=chl&page=1&pageSize=25&sortShowLucene=&isGetxfsd=false&a=1729239163797&isPrecision=True&_=1729239163797
import json
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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    "host": "api.lawdoo.com",
    "origin": "https://lawdoo.com",
    "referer": "https://lawdoo.com/"
}


def make_request(page_index):
    """
    发送 POST 请求并返回响应文本。

    参数:
    page_index (int): 当前页面页数。
    返回:
    str: 响应文本。
    """
    # url = f'https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%2C%2C%2C0%3B60322%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0%2C0%3B0&lib=chl&page={page_index}&pageSize=25&sortShowLucene=&isGetxfsd=false&a=1729239163797&isPrecision=True&_=1729239163797'
    # url = "https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%E5%BB%BA%E8%AE%BE%E9%83%A8+%E5%B7%A5%E7%A8%8B+%E6%8B%9B%E6%A0%87%2C%2C%2C0%3B0%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3BXE0302%2C0%3B0&lib=chl&page=1&pageSize=50&sortShowLucene=&isGetxfsd=false&a=1729840263655&isPrecision=true&_=1729840263655"
    # url = "https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%E5%BB%BA%E8%AE%BE%E9%83%A8+%E5%B7%A5%E7%A8%8B+%E6%8B%9B%E6%A0%87%2C%2C%2C0%3B0%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0012%2C0%3B0&lib=chl&page=1&pageSize=50&sortShowLucene=&a=1730100615896&isPrecision=true&_=1730100615897"
    # url = "https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%E4%B8%93%E5%8D%96%E7%AE%A1%E7%90%86%2C%2C%2C0%3B0%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0%2C0%3B0&lib=chl&page=1&pageSize=50&sortShowLucene=&isGetxfsd=false&a=1730182586297&isPrecision=true&_=1730182586298"
    # url = f'https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%E4%B8%93%E5%8D%96%E7%AE%A1%E7%90%86%2C%2C%2C0%3B0%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0%2C0%3B0&lib=lar&page={page_index}&pageSize=50&sortShowLucene=&isGetxfsd=false&a=1730259073961&isPrecision=true&_=1730259073961'
    # url = f'https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%E4%BB%B7%E6%A0%BC%E7%AE%A1%E7%90%86%2C%2C%2C0%3B0%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0%2C0%3B0&lib=chl&page={page_index}&pageSize=50&sortShowLucene=&a=1730792051963&isPrecision=true&_=1730792051963'
    url = f'https://api.lawdoo.com/api/FD/GetContentTitleList?conditions=%2C%2C%2C0%3B000400100013%2C0%2C-%2C-%2C-%2C0%3B0%2C0%3B0%2C0%3B0&lib=chl&page={page_index}&pageSize=50&sortShowLucene=&a=1731382651704&isPrecision=True&_=1731382651704'
    try:
        ture_headers = headers
        response = requests.get(url, verify=False, headers=ture_headers)
        logger.info(f'连接状态<{response.status_code}>')
        return response.text
    except Exception as e:
        logger.error(f'Exception occurred: {e}')
        return make_request(page_index)


def calculate_dt(data_dict_all):
    title_lt = []
    data_list = data_dict_all.get('TitleList')
    for it in data_list:
        # 标题
        title = it.get('标题')
        title = title.replace('<font class="highlight">', "").replace('</font>', "")
        # id
        title_id = it.get('id')
        fawen = it.get('发文字号')
        bumen = it.get('发布部门')
        if bumen:
            bumen = bumen[0]
        fb_date = it.get('发布日期')
        ss_date = it.get('实施日期')
        xiaoli = it.get('效力级别')
        if xiaoli:
            xiaoli = xiaoli[0]
        shixiao = it.get('时效性')
        title_dt = {
            "标题": title,
            'id': title_id,
            '发文字号': fawen,
            '发布日期': fb_date,
            '实施日期': ss_date,
            '时效性': shixiao,
            '效力级别': xiaoli,
            '发布部门': bumen
        }
        title_lt.append(title_dt)
    return title_lt


def get_title_url():
    all_lt = []
    for it in range(1, 63):
        print(f"第{it}页")
        content = make_request(it)
        # 将JSON字符串转换为字典
        data_dict_all = json.loads(content)
        title_lt = calculate_dt(data_dict_all)
        all_lt += title_lt
    data_df = pd.DataFrame(all_lt)
    return data_df


def clean_string(s):
    return re.sub(r'[\x00-\x1F\x7F]', '', s) if isinstance(s, str) else s


def save_to_excel(dataframe, filename):
    """
    保存DataFrame到Excel文件
    """
    # 清洗 DataFrame 中的所有字符串
    dataframe['标题'] = dataframe['标题'].apply(clean_string)
    with pd.ExcelWriter(filename) as writer:
        dataframe.to_excel(writer, startrow=0, startcol=0,index=False)
    logger.info(f"{filename} 写入完毕！！！")


def calculate(choose=True):
    # 收录内容
    data_df = get_title_url()
    filename = '附件/排查_法器_81.xlsx'
    save_to_excel(data_df, filename)


if __name__ == '__main__':
    calculate()
