import difflib
import random
import re
import time

from elasticsearch import Elasticsearch
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
from botpy import logging
from sqlalchemy import create_engine, text
from query import PublicFunction
import pandas as pd
from retrying import retry
from query.QueryTitle import main_panduan

_log = logging.get_logger()
es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


class TimelinessCheck:
    def __init__(self, **kwargs):
        self.name_r = kwargs.get('负责人')
        self.pf = PublicFunction
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }

    def read_excel_pd(self):
        # 指定Excel文件路径
        file_path = r'C:\Users\admin\Downloads\罗林伟-时效性核对20240902.xls'

        # 读取Excel文件的第一个工作表，并存储为DataFrame
        data_df = pd.read_excel(file_path, engine='xlrd')
        return data_df

    def es_search(self, id):
        """
        传入唯一标志，获取全文内容信息
        :param id:
        :return:
        """
        body = {
            "query": {
                "match": {
                    "_id": id
                }
            }, "stored_fields": ["全文"]
        }
        resp = es.search(body=body)
        full_text_all_lt = resp.get('hits').get('hits')
        if full_text_all_lt:
            full_text = full_text_all_lt[0]
            full_text = full_text.get('fields').get('全文')[0]
            return full_text
        return None

    def add_time_to_date(self, row_date, expiring_time):
        """
        对发布日期进行日期计算,得到失效日期
        :param row_date:
        :param expiring_time:
        :return:
        """
        # 解析日期字符串
        date_format = "%Y.%m.%d"
        date_obj = datetime.strptime(row_date, date_format)
        expiring_time_yr = expiring_time.get('年')
        expiring_time_mt = expiring_time.get('月')
        if expiring_time_yr:
            new_year = date_obj.year + expiring_time_yr
            new_date_str = date_obj.replace(year=new_year).strftime(date_format)
            return new_date_str
        if expiring_time_mt:
            new_year = date_obj.year + expiring_time_mt
            new_date_str = date_obj.replace(year=new_year).strftime(date_format)
            return new_date_str
        return row_date

    def match_validity_period(self, tag_text):
        """
        针对正文中"有效期x年”或者“有效期x月”的情况
        :param tag_text:匹配文本
        :return:
        """
        # 定义正则表达式模式匹配有效期
        pattern_years = re.compile(r'有效期(\d+)年')
        pattern_months = re.compile(r'有效期(\d+)月')

        match_years = pattern_years.search(tag_text)
        match_months = pattern_months.search(tag_text)

        if match_years:
            # 返回年数及其单位
            return {'年': int(match_years.group(1))}
        elif match_months:
            # 返回月数及其单位
            return {'月': int(match_months.group(1))}
        else:
            return None

    def calculate_row(self, row):
        # 初始化状态码
        time.sleep(random.uniform(0, 1))
        row_status = np.nan
        row_id = row.get('唯一标志')
        row_update = row.get('发布日期')
        row_date = row.get('失效日期')
        full_text = self.es_search(row_id)
        full_text_soup = BeautifulSoup(full_text, 'html.parser')
        #
        for tag in full_text_soup:
            tag_text = str(tag)
            if '有效期' in tag_text:
                # 定义正则表达式模式匹配日期
                pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日)')
                match = pattern.search(tag_text)
                if not match:
                    _log.info(f"未能匹配到有效期截止日期: {row['标题']} 中的:\n 匹配文本: {tag_text}")
                    expiring_time = self.match_validity_period(tag_text)
                    if expiring_time:
                        expiring_date = self.add_time_to_date(row_update, expiring_time)
                        if expiring_date == row_date:
                            _log.info(f"[0]失效日期无误: id:{row_id} 标题: {row['标题']}")
                            # 失效日期无误的数据
                            row_status = '0'
                        else:
                            _log.info(f"[10]失效日期有误: id:{row_id} 标题: {row['标题']}")
                            _log.info(f"{row['标题']}文章的原失效日期为:{row_date}  现已修改为: {expiring_date}")
                            row['失效日期'] = expiring_date
                            row_status = '10'
                else:
                    expiring_date = match.group(1)
                    expiring_date = expiring_date.replace('年', '.').replace('月', '.').replace('日', '')

                    if expiring_date == row_date:
                        _log.info(f"[0]失效日期无误: id:{row_id} 标题: {row['标题']}")
                        # 失效日期无误的数据
                        row_status = '0'
                    else:
                        _log.info(f"[10]失效日期有误: id:{row_id} 标题: {row['标题']}")
                        _log.info(f"{row['标题']}文章的原失效日期为:{row_date}  现已修改为: {expiring_date}")
                        row['失效日期'] = expiring_date
                        row_status = '10'
        row['状态'] = row_status
        _log.info("===" * 20)
        return row

    def write_to_excel(self, df):
        # 指定输出Excel文件的路径
        output_file_path = r'E:\JXdata\Python\wan\query\有效性检查输出\output_data.xlsx'

        try:
            # 将DataFrame写入Excel文件
            df.to_excel(output_file_path, index=False)
            print(f"DataFrame已成功写入 {output_file_path}")
        except Exception as e:
            print(f"写入Excel文件时发生错误：{e}")

    def filter_data_df(self, data_df):
        data_df = data_df[data_df['负责人'] == self.name_r]
        data_df['状态'] = np.nan
        data_df = data_df.apply(self.calculate_row, axis=1)
        return data_df

    def calculate(self):
        # 总流程函数
        data_df = self.read_excel_pd()
        data_df = self.filter_data_df(data_df)
        self.write_to_excel(data_df)
        _log.info('处理完毕!!!!!!')


def main_test():
    data_dt = {
        '负责人': "吉祥"
    }
    # 此处为样例传参,保留一个测试用例
    obj = TimelinessCheck(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main_test()
