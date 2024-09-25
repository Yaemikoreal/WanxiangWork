import pyodbc
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine
from query import PublicFunction
import pandas as pd
import logging

from query.decorators import timer

# 配置基本的日志设置
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# 创建一个日志记录器
logger = logging.getLogger('my_logger')


class test2:
    def __init__(self, **kwargs):
        self.pf = PublicFunction
        self.table_name = kwargs.get('table_name')

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

    def write_df_to_sql(self, df, table_name):
        """
        将 DataFrame 分批次写入 SQL Server 数据库中的指定表
        :param df: DataFrame
        :param table_name: 表名
        :return: None
        """
        # 数据库连接信息
        server = '47.97.3.24,14333'
        database = '自收录数据'
        username = 'saa'
        password = '1+2-3..*Qwe!@#'
        driver = '{SQL Server}'
        charset = 'gbk'

        # 构建连接字符串
        connection_string = (
            f'DRIVER={driver};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'UID={username};'
            f'PWD={password};'
            f'charset={charset}'
        )
        # 创建连接
        try:
            conn = pyodbc.connect(connection_string)
        except pyodbc.Error as e:
            logger.error(f"Connection error: {e}")
            return
            # 将 DataFrame 写入数据库
        try:
            cursor = conn.cursor()
            columns = ', '.join([f'[{col}]' for col in df.columns])
            placeholders = ', '.join(['?' for _ in df.columns])

            insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

            for index, row in df.iterrows():
                logger.info(f"{row.get('法规标题')} 正在写入！！")
                cursor.execute(insert_sql, list(row))

            conn.commit()
            # logger.error(f"DataFrame has been successfully written to {table_name}.")
        except pyodbc.Error as e:
            logger.error(f"Error writing DataFrame to {table_name}: {e}")
            conn.rollback()
        finally:
            # 关闭连接
            conn.close()

    def replace_something(self, data_df, content):
        # 定义要替换的HTML标签字符串
        html_tags = '<a data-cmd="tsina" href="#" title="分享到新浪微博"></a><a data-cmd="weixin" href="#" title="分享到微信"></a><a data-cmd="sqq" href="#" title="分享到QQ"></a><a data-cmd="mail" href="#" title="分享到邮件分享"></a><a data-cmd="print" href="#" title="分享到打印"></a><a data-cmd="copy" href="#" title="分享到复制网址"></a>'
        # 使用正则表达式替换掉HTML标签
        data_df[content] = data_df[content].str.replace(html_tags, '', regex=True)
        # 应用函数
        data_df[content] = data_df[content].apply(self.calculate_right)
        return data_df

    def calculate_right(self, str_text):
        soup = BeautifulSoup(str_text, 'html.parser')
        soup = self.pf.add_right(soup, ['年', '月', '日'])
        soup = self.pf.add_right(soup, ['局', '会'])

        a_all = soup.find_all('a', href=True)
        for a in a_all:
            a['href'] = ''.join(f"/datafolder/新收录/{datetime.now().strftime('%Y%m')}/{a.get_text()}")
        text_return = str(soup)
        return text_return

    def write_to_oa(self, it):
        sql = rf"INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES ('{it['唯一标志']}','{it.get('法规标题')}','{it['全文']}','{it['发布部门']}','{it['类别']}','{it.get('发布日期')}','{it['效力级别']}','{it['实施日期']}','{it['发文字号']}','{it['时效性']}','{it['来源']}','{it['收录时间']}')"
        self.pf.save_sql_BidDocument(sql)
        print(f"写入成功: {it.get('法规标题')}")
        logger.info(f"{sql}")

    @timer
    def calculate(self):
        data_df = self.from_mysql(self.table_name)
        data_df = data_df.drop(columns=['ID'])
        data_df = data_df.drop(columns=['收录来源个人'])
        # 将 '发文字号' 列的数据类型转换为字符串类型
        data_df['发文字号'] = data_df['发文字号'].astype(str)
        # 删除所有值为空的列
        data_df = data_df.dropna(axis=1, how='all')
        shoulu_date = "JX" + str(datetime.now().strftime("%Y.%m.%d"))
        data_df['收录时间'] = shoulu_date

        try:
            # self.write_df_to_sql(data_df, "专项补充收录")
            data_df.apply(self.write_to_oa, axis=1)
            logger.info("写入成功！！！")
        except Exception as e:
            logger.error(f"df写入错误： {e}")


def main():
    data_dt = {
        "table_name": '专项补充收录二次修改',
    }
    obj = test2(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main()