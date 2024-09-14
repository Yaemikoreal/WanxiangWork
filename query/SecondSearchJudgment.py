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
        self.write_table_real = kwargs.get('write_table_real')

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
        any_issued_number = row.get('发文字号')
        any_issued_date = row.get('发布日期')
        if pd.isna(any_issued_number):
            if main_panduan(any_title, issued_date=any_issued_date):
                # _log.info(f"法器地方法规有这条数据： {any_title}")
                return False
            _log.info(f"法器地方法规没有这条数据： {any_title}")
            return True
        if main_panduan(any_title, issued_number=any_issued_number, issued_date=any_issued_date):
            # _log.info(f"法器地方法规有这条数据： {any_title}")
            return False
        _log.info(f"法器地方法规没有这条数据： {any_title}")
        return True

    def process_row_clean(self, row):
        title = row.get('法规标题')
        excluded_keywords = {
            '公告', '通报', '通告', '公示', '政策解读', '答记者问', '资质审批名单', '征求意见稿', '备案', '面试名单',
            '工作', '培训会', '核准', '公布表', '获批', '予以备案', '备案公告', '报告', '资源包下载', '评估',
            '活动情况', '诉求清单', '聘用', '招聘启事', '人员启事', '招聘人员面试', '招聘', '征稿', '遴选', '测试成绩',
            '予以同意', '法人变更', '业主变更', '政策提示', '预算表'}
        excluded_suffixes = {
            '公告', '通报', '通告', '公示', '政策解读', '答记者问', '资质审批名单', '征求意见稿', '备案', '面试名单',
            '工作', '培训会', '核准', '公布表', '获批', '予以备案', '备案公告', '报告', '资源包下载', '评估',
            '活动情况', '诉求清单', '招聘简章', '予以同意', '分数线', '立项'}
        department_not_dt = {
            '国务院'
        }
        # 检查是否包含排除关键字
        if any(keyword in title for keyword in excluded_keywords):
            return False
        # 检查是否以排除后缀结尾
        if any(title.endswith(suffix) for suffix in excluded_suffixes):
            return False
        # 检查部门信息
        if any(keyword in title for keyword in department_not_dt):
            return False
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

    def title_calculate(self, row):
        """
        对每一行的标题进行异常值处理，并针对处理发文字号
        :param row:
        :return:
        """
        title_s = row.get("法规标题")
        title_s = title_s.replace('?', '')
        issued_number_yuan = row.get("发文字号")
        if not issued_number_yuan:
            # 正则表达式匹配发文字号
            pattern = r'\（([^）]+)号\）$'
            match = re.search(pattern, title_s)
            if match:
                issued_number = match.group(1) + '号'
                row['发文字号'] = issued_number
        row['法规标题'] = title_s
        return row

    def date_calculate(self, row, soup):
        """
        尝试用正文和标题内容获取发布日期
        :param row:
        :param soup:
        :return:
        """
        not_lt = ["第", "年"]
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
        if row.get("发文字号"):
            if isinstance(row, str):
                for it in not_lt:
                    if it in row.get("发文字号"):
                        row["发文字号"] = None
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

        for tag in soup.find_all(True):
            attrs_to_remove = ['class']
            for attr in attrs_to_remove:
                # tag.attrs 包含了标签的所有class属性
                if attr in tag.attrs:
                    del tag[attr]
        row['全文'] = str(soup)

        # 尝试用正文和标题内容获取发文字号和发布日期
        row = self.date_calculate(row, soup)
        # 发文字号
        row = self.issued_number_calculate(row, soup)
        _log.info(f"{row.get('法规标题')} 处理完成！")
        return row

    def clean_dataframe(self):
        filtered_df = self.data_df
        filtered_df = filtered_df[filtered_df.apply(self.process_row_clean, axis=1)]
        # 处理“时效性”列中的空值,填充为默认 01
        filtered_df['时效性'] = filtered_df['时效性'].fillna('01')

        # 处理法规标题的异常值
        filtered_df = filtered_df.apply(self.title_calculate, axis=1)
        # 针对法规标题进行去重处理
        filtered_df = filtered_df.drop_duplicates(subset='法规标题', keep='first')
        # 针对正文内容进行标签值的最终处理
        filtered_df = filtered_df.apply(self.text_calculate, axis=1)

        # 处理发布日期和实施日期的异常值
        filtered_df['发布日期'] = filtered_df['发布日期'].apply(lambda x: self.check_date_format(x))
        filtered_df['实施日期'] = filtered_df['实施日期'].apply(lambda x: self.check_date_format(x))

        filtered_df['发文字号'] = filtered_df['发文字号'].replace({None: ''})
        return filtered_df

    def calculate(self):
        write_name_real = self.write_table_real
        if self.data_df.empty:
            # 过滤系统是否有该一系列文件
            self.data_df = self.from_mysql(write_name_real)
        # self.data_df = self.data_df[self.data_df['收录来源个人'] == '重庆市生态环境局']
        # 对df的内容进行最后清洗

        filtered_df = self.clean_dataframe()
        filtered_df = self.article_cleaning(filtered_df)
        # 获取行数
        num_rows = filtered_df.shape[0]
        _log.info(f"  文件二次过滤完毕,需要写入  {num_rows}条!!!")

        if not self.write_table:
            # 删除ID列
            filtered_df = filtered_df.drop(columns=['ID'])
            filtered_df = filtered_df[filtered_df['发布日期'].notnull()]
            self.pf.to_mysql(filtered_df, write_name_real + '_new')
            _log.info(f" 已经写入{write_name_real}_new表!!!")
        return filtered_df


def main(data_df=None, write_table=None):
@timer
def main(data_df=pd.DataFrame(), write_table=None):
    """

    :param data_df: 传入的需要处理的df
    :param write_table: 传入的需要写入的df地址
    :return:
    """
    # 指定表进行处理的表名(正常调用请勿传参）
    write_table_real = '重庆市其他文件'
    data_dt = {
        "write_table": write_table,
        'data_df': data_df,
        'write_table_real': write_table_real
    }
    obj = Judgment(**data_dt)
    filtered_df = obj.calculate()
    return filtered_df


if __name__ == '__main__':
    main()
