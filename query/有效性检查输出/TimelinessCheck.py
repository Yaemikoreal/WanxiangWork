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

    def check_date_format(self, date_str):
        """
        检查给定的字符串是否符合'YYYY.MM.DD'格式。
        如果符合，则返回该日期，否则返回NaN。
        """
        try:
            if date_str:
                if not pd.isna(date_str):
                    # 解析输入的日期字符串
                    date_obj = datetime.strptime(date_str, '%Y.%m.%d')
                    # 格式化日期对象为新的字符串格式
                    formatted_date = date_obj.strftime('%Y.%m.%d')
                    return formatted_date
            return None
        except ValueError:
            # 如果转换失败，则返回NaN
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
            new_date_str = self.check_date_format(new_date_str)
            return new_date_str
        if expiring_time_mt:
            new_year = date_obj.year + expiring_time_mt
            new_date_str = date_obj.replace(year=new_year).strftime(date_format)
            new_date_str = self.check_date_format(new_date_str)
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

    @staticmethod
    def format_expiring_date(date_str):
        return date_str.replace('年', '.').replace('月', '.').replace('日', '')

    def update_status_and_log(self, row, row_date, expiring_date_lt, tag_text, row_status):
        not_in_dt = {'起执行', '起实施', '起施行'}
        for expiring_date in expiring_date_lt:
            if expiring_date == row_date:
                if "同时废止" in tag_text:
                    _log.info(f"[13]失效日期无误,文章内容有描述其他文件续期或者失效的: 标题: {row['标题']}")
                    _log.info(
                        f"[13] {row['标题']} 文章的 发布日期为:{row['发布日期']}    原失效日期为:{row_date}  匹配到的日期为:{expiring_date}")
                    _log.info(f"[13]匹配的内容文本为: {tag_text}")
                    row_status = '13'
                else:
                    _log.info(f"[0]失效日期无误: 标题: {row['标题']}")
                    _log.info(
                        f"[0] {row['标题']} 文章的 发布日期为:{row['发布日期']}    原失效日期为:{row_date} 匹配到的日期为:{expiring_date}")
                    _log.info(f"[0]匹配的内容文本为: {tag_text}")
                    row_status = '0'
            else:
                # if "同时废止" in tag_text:
                #     _log.info(f"[14]失效日期有误,文章内容有描述其他文件续期或者失效的:  标题: {row['标题']}")
                #     _log.info(f"[14] {row['标题']}文章的原失效日期为:{row_date}  现已修改为: {expiring_date}")
                #     _log.info(f"[14]匹配的内容文本为: {tag_text}")
                #     row['失效日期'] = expiring_date
                #     row_status = '14'
                # else:
                #     _log.info(f"[10]失效日期有误:  标题: {row['标题']}")
                #     _log.info(f"[10] {row['标题']}文章的原失效日期为:{row_date}  现已修改为: {expiring_date}")
                #     _log.info(f"[10]匹配的内容文本为: {tag_text}")
                #     row['失效日期'] = expiring_date
                #     row_status = '10'
                pass
        return row_status

    def get_largest_date(self, dates):
        formatted_dates = [self.format_expiring_date(date) for date in dates]
        largest_date = max(formatted_dates, key=lambda d: [int(part) for part in d.split('.')])
        largest_date = self.check_date_format(largest_date)
        return largest_date

    def calculate_date_r(self, tag_text, row_update, row, row_date, row_status):
        expiring_time = self.match_validity_period(tag_text)
        if expiring_time:
            expiring_date_r = self.add_time_to_date(row.get('实施日期'), expiring_time)
            expiring_date = self.add_time_to_date(row_update, expiring_time)
            expiring_date_lt = [expiring_date_r, expiring_date]
            row_status = self.update_status_and_log(row, row_date, expiring_date_lt, tag_text, row_status)
        else:
            _log.error(f"未能匹配到有效期截止日期: {row['标题']} 中的:\n 匹配文本为: {tag_text}")
        return row_status

    def calculate_row(self, row):
        # 初始化状态码
        # time.sleep(random.uniform(0, 1))  # 如果不需要延迟，可以注释掉这行
        row_status = np.nan
        row_id = row.get('唯一标志')
        row_update = row.get('发布日期')
        row_date = row.get('失效日期')
        full_text = self.es_search(row_id)
        full_text_soup = BeautifulSoup(full_text, 'html.parser')

        # 定义正则表达式模式匹配日期
        pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日)')

        if row['标题'] == '福州市人民政府办公厅关于印发福州市建筑业招商培育专项工作实施方案的通知':
            time.sleep(1)
            print(1)
        for tag in full_text_soup.stripped_strings:
            tag_text = str(tag)
            if '有效期' in tag_text:
                matches = pattern.findall(tag_text)
                if matches:
                    if "有效期至" in tag_text:
                        expiring_date = [self.get_largest_date(matches)]
                        row_status = self.update_status_and_log(row, row_date, expiring_date, tag_text, row_status)
                    else:
                        row_status = self.calculate_date_r(tag_text, row_update, row, row_date, row_status)
                else:
                    row_status = self.calculate_date_r(tag_text, row_update, row, row_date, row_status)
            if row_status is not np.nan:
                row['状态'] = row_status
                _log.info("===" * 20)
                return row
        return row

    def write_to_excel(self, df):
        # 指定输出Excel文件的路径
        output_file_path = r'/query/有效性检查输出/output_data.xlsx'

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
