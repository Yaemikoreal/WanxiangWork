import re
from datetime import datetime
import numpy as np
from retrying import retry
from query.QueryTitle import main_panduan
from sqlalchemy import create_engine
from query import PublicFunction
import pandas as pd
from botpy import logging
from bs4 import BeautifulSoup

"""
行政规范性文件
本方法用于将库中内容读出，根据信息再次确定系统是否缺失该条数据
"""
_log = logging.get_logger()


class Judgment:
    def __init__(self, **kwargs):
        self.data_df = kwargs.get('data_df')
        self.pf = PublicFunction
        self.write_table = kwargs.get('write_table')

    def from_mysql(self, table_name):
        """
        从 MySQL 读取数据并返回 DataFrame
        :param table_name: 表名
        :return: DataFrame
        """
        # 数据库连接信息
        server = 'localhost'
        database = 'test'
        # Integrated Security=True启用Windows身份验证
        connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
        # 创建连接
        try:
            engine = create_engine(connection_string)
        except Exception as e:
            print(f"Connection error: {e}")
            return None
        # 读取表数据
        try:
            df = pd.read_sql_table(table_name, con=engine)
        except Exception as e:
            print(f"Error reading table {table_name}: {e}")
            df = None
        # 关闭连接
        engine.dispose()
        return df

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

    @retry(stop_max_attempt_number=3)
    def process_row(self, row):
        any_title = row['法规标题']
        any_issued_number = row['发文字号']
        any_issued_date = row['发布日期']
        if not any_issued_date:
            any_w = row['全文']
        if main_panduan(any_title, issued_number=any_issued_number, issued_date=any_issued_date):
            # _log.info(f"法器地方法规有这条数据： {any_title}")
            return False
        _log.info(f"法器地方法规没有这条数据： {any_title}")
        return True

    def article_cleaning(self, filtered_df):
        """
        根据文章的标题，发文字号，发布日期
        对文章进行二次判断，以确定系统是否真的确实该文件
        :return: filtered_df
        """
        data_df = filtered_df
        # 删除所有值为空的列
        data_df = data_df.dropna(axis=1, how='all')
        # 使用 apply() 并保留布尔值为 True 的行
        filtered_df = data_df[data_df.apply(self.process_row, axis=1)]
        return filtered_df

    def title_calculate(self, title_s):
        """
        对每一行的标题进行异常值处理
        :param title_s:
        :return:
        """
        title_s = title_s.replace('?', '')
        return title_s

    def date_calculate(self, row, soup):
        """
        尝试用正文和标题内容获取发布日期
        :param row:
        :param soup:
        :return:
        """
        # 发布日期
        date_value = row.get('发布日期')
        if not date_value:
            row_text = soup.get_text()

            pattern = r"(\d{4})\D*年\D*(\d{1,2})\D*月\D*(\d{1,2})\D*日"
            # 使用 findall 方法查找所有匹配项
            matches = re.findall(pattern, row_text)
            if matches:
                for match in matches:
                    year = match[0]
                    month = match[1]
                    day = match[2]
                    if month == '0' or day == '0':
                        continue
                    date = f"{year}.{month}.{day}"
                    row['发布日期'] = date
                    row['实施日期'] = row['发布日期']
                    if row['发布日期']:
                        break

        return row

    def issued_number_calculate(self, row, soup):
        """
        尝试用正文和标题内容获取发文字号
        :param row:
        :param soup:
        :return:
        """
        issued_number_value = row.get('发文字号')
        if not issued_number_value:
            row_text = soup.get_text()
            title = row.get('法规标题')
            if "号" in title:
                # 正则表达式模式
                pattern = r"\（([^\（\）]+)\〔(\d{4})\〕(\d{1,2})号\）"
                # 使用 search 方法查找第一个匹配项
                match = re.search(pattern, title)
                if match:
                    full_code = f"{match.group(1)}〔{match.group(2)}〕{match.group(3)}号"
                    row["发文字号"] = full_code
        return row

    def text_calculate(self, row):
        """
        针对全文进行格式化再次处理,尝试用正文和标题内容获取发文字号和发布日期
        :param row: df的一行
        :return:
        """
        not_dt = {"text-align:right", "text-align:center", "text-align: right", 'text-align: center', 'id'}
        text_q = row.get('全文')
        soup = BeautifulSoup(text_q, 'html.parser')
        # 遍历所有标签节点
        for tag in soup.find_all(recursive=True):
            style_s = tag.find_all('style')
            for it in style_s:
                del tag[it]

            # 去除掉重复的style值
            if tag.has_attr('style'):
                style = tag.get('style')
                styles = [s.strip() for s in style.split(';') if s.strip()]
                if styles:
                    if styles[0] in not_dt:
                        tag['style'] = styles[0]
        row['全文'] = str(soup)

        # 尝试用正文和标题内容获取发文字号和发布日期
        row = self.date_calculate(row, soup)
        # 发文字号
        row = self.issued_number_calculate(row, soup)
        _log.info(f"{row.get('法规标题')} 处理完成！")
        return row

    def clean_dataframe(self):
        filtered_df = self.data_df
        # 处理“时效性”列中的空值,填充为默认 01
        filtered_df['时效性'] = filtered_df['时效性'].fillna('01')
        # 删除ID列
        filtered_df = filtered_df.drop(columns=['ID'])
        # 处理法规标题的异常值
        filtered_df['法规标题'] = filtered_df['法规标题'].apply(lambda x: self.title_calculate(x))
        # 针对法规标题进行去重处理
        filtered_df = filtered_df.drop_duplicates(subset='法规标题', keep='first')
        # 针对正文内容进行标签值的最终处理
        filtered_df = filtered_df.apply(self.text_calculate, axis=1)

        # 处理发布日期和实施日期的异常值
        filtered_df['发布日期'] = filtered_df['发布日期'].apply(lambda x: self.check_date_format(x))
        filtered_df['实施日期'] = filtered_df['实施日期'].apply(lambda x: self.check_date_format(x))
        return filtered_df

    def calculate(self):
        # 过滤系统是否有该一系列文件
        self.data_df = self.from_mysql('重庆市其他文件')
        # self.data_df = self.data_df[self.data_df['收录来源个人'] == '重庆市生态环境局']
        # 对df的内容进行最后清洗
        filtered_df = self.clean_dataframe()
        filtered_df = self.article_cleaning(filtered_df)

        # 获取行数
        num_rows = filtered_df.shape[0]
        _log.info(f"  文件二次过滤完毕,需要写入  {num_rows}条!!!")

        self.pf.to_mysql(filtered_df, self.write_table)
        _log.info(f"写入{self.write_table}完毕!!!")
        return filtered_df


def main(data_df=None):
    data_dt = {
        "write_table": '重庆市其他文件_new',
    }
    obj = Judgment(**data_dt)
    filtered_df = obj.calculate()


if __name__ == '__main__':
    main()
