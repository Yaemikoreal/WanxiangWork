import time
import random
import requests
from bs4 import BeautifulSoup, NavigableString, Comment
import hashlib
import pandas as pd
from sqlalchemy import create_engine, text
import re
import pyodbc
from botpy import logging
from query.QueryTitle import main_panduan
from CQWushan import WushanFuhan
_log = logging.get_logger()
"""
本方法用于获取重庆市司法局行政规范性文件

url:https://sfj.cq.gov.cn/zwgk_243/zfxxgkml1/zcwj/sfjgfxwj/xzgfxwj/index.html
"""


class Judiciary:
    def __init__(self):
        #
        self.ws = WushanFuhan.WushanStandardizedDocuments()
        # 初始url
        self.start_url = 'https://sfj.cq.gov.cn/zwgk_243/zfxxgkml1/zcwj/sfjgfxwj/xzgfxwj/index.html'
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        # 保留列表
        self.into_lt = ["text-align:right", "text-align:center", "text-align: right"]
        # 发布部门
        self.department_of_publication = "8;831;83103;831030007"  # 重庆市司法局
        # 类别
        self.category = {"机关工作综合规定": "003;00301"}
        # 效力级别
        self.level_of_effectiveness = {"地方规范性文件": "XP08", "地方工作文件": "XP10"}

    def fetch_url(self, url):
        """
        获取网页信息内容
        cl_num:重试次数为3
        :param url:
        :return: soup
        """
        cl_num = 3
        for it in range(cl_num):
            try:
                sleep = random.uniform(0, 2)
                _log.info(f"休眠{sleep}秒")
                time.sleep(sleep)
                # 发送 HTTP GET 请求
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                if response.status_code == 200:
                    # 返回页面内容
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return soup
            except pyodbc.OperationalError as e:
                _log.info(f"出错！      {e}")
                sleep = random.uniform(2, 4)
                _log.info(f"休眠{sleep}秒")
                time.sleep(sleep)
                _log.info("==========================")
                if it == cl_num - 1:
                    _log.info("该网站内容无法获取")
                    _log.info(f"网站url:  {url}")
        return soup

    def remove_outer_brackets(self, text_remove, end_phrase):
        """
        删除字符串开头和结尾的括号，并保留 发文字号,并删除发文日期
        :param text_remove:
        :param end_phrase:
        :return: 发文字号
        """
        # 移除开头的括号
        if text_remove.startswith('('):
            text_remove = text_remove[1:]
        # 移除结尾的括号
        if text_remove.endswith(')'):
            text_remove = text_remove[:-1]
        # 找到 "发文字号：" 的结束位置
        start_phrase_end = text_remove.find("：", text_remove.find("发文字号"))
        start_index = start_phrase_end + 1
        # 找到 "成文日期" 的开始位置
        end_phrase_start = text_remove.find(end_phrase)
        if end_phrase_start == -1:
            return text_remove  # 如果没有找到结束短语，则返回原字符串
        # 返回 "发文字号：" 和 "成文日期" 之间的文本
        result = text_remove[start_index:end_phrase_start]
        return result

    def title_data_get(self, url):
        """
        用于获取到总页面内容，获取到该页的 标题，发文字号，成文日期
        :return:result_lt：列表套字典，字典装有信息
        """
        result_lt = []
        # 获取到总网页内容
        soup_title_all = self.fetch_url(url)
        soup_title_all = soup_title_all.find('table', class_='zcwjk-list')
        soup_title_all = soup_title_all.find_all('tr', class_=['zcwjk-list-c clearfix', 'zcwjk-list-c clearfix cur'])
        for tag in soup_title_all:
            title_get = tag.find('p', class_='tit')
            # 标题
            title = title_get.get_text()
            title_url_get = tag.find('a', target="_blank")
            # url 未拼接
            title_url = title_url_get.get('href')
            issued_num_get = tag.find('p', class_='info')
            # 发文字号
            issued_num = issued_num_get.get_text()
            issued_num = self.remove_outer_brackets(issued_num, "成文日期 ")
            issued_date = issued_num_get.find('span', class_='time').get_text()
            # 发布日期
            issued_date = issued_date.lstrip("成文日期 ：")
            issued_date = issued_date.replace("年", ".").replace("月", ".").replace("日", ".")
            data_dt = {
                "法规标题": title,
                "法规url": title_url,
                "发文字号": issued_num,
                "发布日期": issued_date
            }
            result_lt.append(data_dt)
        return result_lt

    def filter(self, result_lt):
        new_result_lt = []
        for result in result_lt:
            title = result.get('法规标题')
            issued_number = result.get('发文字号')
            if main_panduan(title, issued_number):
                # 为Ture则说明该文章已经存在
                continue
            new_result_lt.append(result)
        return new_result_lt

    def zhengwen_get(self, soup):
        # 正文
        class_lt = ['trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_external'
                    ]
        zhengwen = soup.find('div', class_='zcwjk-xlcon')
        for it in class_lt:
            zhengwen_stat = zhengwen.find('div', class_=it)
            if zhengwen_stat is not None:
                break
        # 对style标签值进行处理
        if zhengwen:
            soup_ture = self.ws.soup_cal(zhengwen)
            soup_ture = self.ws.remove_nbsp(soup_ture)
        else:
            soup_ture = None
        soup_ture = str(soup_ture)
        return soup_ture

    def to_mysql(self, df, table_name):
        # 数据库连接信息
        server = 'localhost'
        database = 'test'
        # Integrated Security=True启用Windows身份验证
        connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
        # 创建连接
        try:
            engine = create_engine(connection_string)
        except pyodbc.OperationalError as e:
            _log.info(f"Connection error: {e}")
            exit()
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    def filter_all(self, new_result_lt):
        for it in new_result_lt:
            _log.info(f"需要写入的文章:{it.get('法规标题')}")
            _log.info("============================================")
            new_get_url = self.start_url.rstrip('index.html') + it.get('法规url').lstrip('./')
            # soup
            soup = self.fetch_url(new_get_url)
            # 正文
            zhengwen = self.zhengwen_get(soup)
            it['全文'] = zhengwen
            # 唯一标志
            md5_str = it.get('法规标题') + it.get('发布日期')
            md5_value = self.ws.get_md5(md5_str)
            it["唯一标志"] = md5_value
            # 来源
            it["来源"] = new_get_url
            # 发布部门 重庆市司法局
            it["发布部门"] = self.department_of_publication
            # 类别
            leibie = self.category['机关工作综合规定']
            it["类别"] = leibie
            # 效力级别
            xiaoli = self.level_of_effectiveness['地方规范性文件']
            it["效力级别"] = xiaoli
            # 时效性
            shixiao = "01"
            it["时效性"] = shixiao
            it["实施日期"] = it.get('发布日期')
            del it['法规url']
            return new_result_lt
    def calculate(self):
        for i in range(3):
            if i == 0:
                new_url = self.start_url
            else:
                new_url = f"https://sfj.cq.gov.cn/zwgk_243/zfxxgkml1/zcwj/sfjgfxwj/xzgfxwj/index_{i}.html"
            # 获取该页内容信息
            result_lt = self.title_data_get(url=new_url)
            # 过滤已有的文章
            new_result_lt = self.filter(result_lt)
            if not new_result_lt:
                _log.info(f"第{i + 1}页    无内容需要写入！！！")
                continue
            _log.info(f"第{i+1}页    需要写入的文章有 {len(new_result_lt)} 篇！！！")
            # 统筹整理数据
            new_result_lt = self.filter_all(new_result_lt)
            data_df = pd.DataFrame(new_result_lt)
            self.to_mysql(data_df,'chlour')
            _log.info(f"第{i + 1}页    写入完毕！！！")



def main():
    obj = Judiciary()
    obj.calculate()


if __name__ == '__main__':
    main()
