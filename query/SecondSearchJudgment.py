from retrying import retry
from query.QueryTitle import main_panduan
from sqlalchemy import create_engine
from query import PublicFunction
import pandas as pd
from botpy import logging

"""
行政规范性文件
本方法用于将库中内容读出，根据信息再次确定系统是否缺失该条数据
"""
_log = logging.get_logger()


class Judgment:
    def __init__(self, **kwargs):
        self.data_df = kwargs.get('data_df')
        self.pf = PublicFunction

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

    @retry(stop_max_attempt_number=3)
    def process_row(self, row):
        any_title = row['法规标题']
        any_issued_number = row['发文字号']
        any_issued_date = row['发布日期']
        if main_panduan(any_title, issued_number=any_issued_number, issued_date=any_issued_date):
            _log.info(f"法器地方法规有这条数据： {any_title}")
            return False
        return True

    def article_cleaning(self):
        """
        根据文章的标题，发文字号，发布日期
        对文章进行二次判断，以确定系统是否真的确实该文件
        :return: filtered_df
        """
        data_df = self.data_df
        # 删除所有值为空的列
        data_df = data_df.dropna(axis=1, how='all')
        # 使用 apply() 并保留布尔值为 True 的行
        filtered_df = data_df[data_df.apply(self.process_row, axis=1)]
        _log.info("过滤完毕!!!")

        return filtered_df

    def clean_dataframe(self, filtered_df):
        # 处理“时效性”列中的空值,填充为默认 01
        filtered_df['时效性'] = filtered_df['时效性'].fillna('01')
        filtered_df = filtered_df.drop(columns=['ID'])
        return filtered_df

    def calculate(self):
        # 过滤系统是否有该一系列文件
        filtered_df = self.article_cleaning()
        # 对df的内容进行最后清洗
        filtered_df = self.clean_dataframe(filtered_df)
        # self.pf.to_mysql(filtered_df, self.write_table)
        # _log.info(f"写入{self.write_table}完毕!!!")
        return filtered_df


def main(data_df=None):
    data_dt = {
        "data_df": data_df,
    }
    obj = Judgment(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main()
