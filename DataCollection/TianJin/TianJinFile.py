import difflib
import json
import random
import re
import time

from elasticsearch import Elasticsearch
import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
from botpy import logging
from sqlalchemy import create_engine, text
from query import PublicFunction
import pandas as pd
from query.SecondSearchJudgment import main as main_df_cal
from retrying import retry
from query.QueryTitle import main_panduan

logger = logging.get_logger()
es_client = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


class TianJinFile:
    def __init__(self):
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        self.pf = PublicFunction

    def soup_cal(self, soup_ture):
        """
        传入正文部分soup，传出初步清洗的结果soup
        :param soup_ture:
        :return:
        """
        not_dt = {"text-align:right", "text-align:center", "text-align: right", 'text-align: center', 'id'}

        def process_style(tag_s):
            style = tag_s.get('style')
            if style:
                styles = [s.strip() for s in style.split(';') if s.strip()]
                new_styles = []
                for s in styles:
                    # 如果样式是 text-align:end 或 text-align: end，则替换为 text-align:right
                    if s.startswith('text-align:end') or s == 'text-align: end':
                        s = 'text-align:right'
                    if s in not_dt or s.startswith('text-align:right'):
                        new_styles.append(s)

                if new_styles:
                    tag_s['style'] = '; '.join(new_styles)
                else:
                    del tag_s['style']

        for tag in soup_ture.find_all(True):
            attrs_to_remove = ['data-index', 'id', 'class', 'type', 'new', 'times', 'lang', 'clear', 'content',
                               'http-equiv', 'rel']
            for attr in attrs_to_remove:
                if attr == 'class' and 'class' in tag.attrs:
                    class_value = tag.get('class')
                    if class_value == ["alink"]:
                        continue
                # tag.attrs 包含了标签的所有属性
                if attr in tag.attrs:
                    del tag[attr]
            process_style(tag)
        # # 处理可能的顶级元素样式
        process_style(soup_ture)
        return soup_ture

    def remove_nbsp(self, soup):
        """
        对初步清洗的soup进行进步格式清洗
        :param soup: 初步清洗的soup
        :return: 最终结果
        """
        # 遍历所有的文本节点
        for tag in soup.find_all(True):
            if tag.string and isinstance(tag.string, NavigableString):
                # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
                # 将非换行空格替换为空格
                new_string = tag.string.replace(' ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(' ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace('  ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(" ", " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace("  ", " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(" ", " ")
                tag.string.replace_with(new_string)
        a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
        soup = BeautifulSoup(a.sub(' ', str(soup)), "html.parser")

        remove_text_lt = ['span', 'video']
        for it_t in remove_text_lt:
            # 遍历所有的对应标签
            for span in soup.find_all(it_t):
                # 如果对应标签的文本为空，则移除它
                if not span.get_text().strip():
                    span.decompose()

        # 如果有抄送，删除抄送
        for it in soup.find_all('p'):
            tag_text = it.get_text()
            if "抄送" in tag_text:
                it.decompose()

        # 删除法宝新AI
        for it in soup.find_all('a', logfunc='法宝新AI'):
            it.decompose()
        # 删除本法变迁
        for it in soup.find_all('a', logfunc='本法变迁'):
            it.decompose()
        # 将 soup 转换为字符串
        html_str = str(soup)
        # 使用正则表达式移除 HTML 注释
        html_str_without_comments = re.sub(r'<!--(.*?)-->', '', html_str, flags=re.DOTALL)
        # 重新解析成一个新的 soup 对象
        soup = BeautifulSoup(html_str_without_comments, 'html.parser')
        return soup

    def check_elasticsearch_existence(self, title, index):
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
        response = es_client.search(index=index, body=query_body)
        if int(response['hits']['total']) == 0:
            logger.info(f'文章不存在: {title}')
            return True
        else:
            logger.info(f'存在文章: {title}')
            return False

    def cal_data_dt(self, data_dt):
        data_lt = []
        content_lt = data_dt.get('page', {}).get('content', [])
        if content_lt:
            for it in content_lt:
                title = it.get('title')
                title = re.sub(r'</?em>', '', title)
                any_dt = {
                    "标题": title,
                    "发文字号": it.get('wh'),
                    "url": it.get('url')
                }
                if self.check_elasticsearch_existence(title, 'lar'):
                    data_lt.append(any_dt)
        return data_lt

    def get_top_msg(self, top_tag):
        top_msg_dt = {}
        title_tags = top_tag.find_all('div', attrs={'class': 'sx-item'})
        for it in title_tags:
            key_title = it.find('div', attrs={'class': 'sx-title'})
            key_str = key_title.get_text().replace('　　　 ', '').replace('：', '')
            value_title = it.find('div', attrs={'class': 'sx-con'})
            value_str = value_title.get_text()
            top_msg_dt[key_str] = value_str
        return top_msg_dt

    def get_fulltext(self, data_lt):
        for it in data_lt:
            content_url = it.get('url')
            soup = self.pf.fetch_url(content_url, self.headers)
            fulltext_tag = soup.find('div', attrs={'class': 'xl-zw-con'})

            top_tag = fulltext_tag.find('div', attrs={'class': 'top-container'})
            top_msg_dt = self.get_top_msg(top_tag)

            full_tag = fulltext_tag.find('div', attrs={'class': 'view TRS_UEDITOR trs_paper_default trs_word'})
            full_tag = self.soup_cal(full_tag)
            full = self.remove_nbsp(full_tag)

            print(1)

    def get_title_and_url(self):
        for it in range(1, 6):
            time.sleep(random.uniform(0.5, 1.25))
            connect_url = f" https://scjg.tj.gov.cn/igs/front/search.jhtml?code=6b673dab567a4589b77308e18aad996b&pageNumber={it}&pageSize=10&queryAll=true&searchWord=%E8%A3%81%E9%87%8F%E6%9D%83%E5%9F%BA%E5%87%86&siteId=43"
            response = requests.get(connect_url, self.headers)
            response_text = response.text
            data_dt = json.loads(response_text)

            data_lt = self.cal_data_dt(data_dt)
            self.get_fulltext(data_lt)

    def calculate(self):
        self.get_title_and_url()
        print(1)
        pass


def main():
    obj = TianJinFile()
    obj.calculate()


if __name__ == '__main__':
    main()
