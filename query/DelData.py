import pandas as pd

from query import PublicFunction
import logging
from decorators import timer
import pyodbc
from SecondSearchJudgment import main as clean_cal
# 创建一个日志记录器
logger = logging.getLogger('my_logger')


class test3:
    def __init__(self, **kwargs):
        self.del_table = kwargs.get("del_table")
        self.pf = PublicFunction
        self.shoulu_date = kwargs.get("shoulu_date")
        self.connection_string = (
            'DRIVER={SQL Server};'
            'SERVER=47.97.3.24,14333;'
            'DATABASE=自收录数据;'
            'UID=saa;'
            'PWD=1+2-3..*Qwe!@#;'
            'charset=gbk'
        )

    @timer
    def del_to_oa(self, sql):
        self.pf.save_sql_BidDocument(sql)

    def execute_query(self, sql):
        # sql = f"SELECT * FROM [dbo].[{self.del_table}] WHERE [收录时间] LIKE '%JX%'"

        # 建立数据库连接
        conn = pyodbc.connect(self.connection_string)

        try:
            # 执行SQL查询并将结果转换为DataFrame
            df = pd.read_sql(sql, conn)
            print("查询结果已成功转换为DataFrame:")
            return df
        except Exception as e:
            print(f"查询失败: {e}")
        finally:
            # 关闭数据库连接
            conn.close()

    def calculate(self):
        # shoulu_date = "JX" + self.shoulu_date
        sql = f"SELECT * FROM [dbo].[{self.del_table}] WHERE [收录时间] LIKE '%JX%'"
        # sql = f"DELETE FROM [dbo].[{self.del_table}] WHERE [收录时间] = '{shoulu_date}';"
        # self.del_to_oa(sql)
        data_df = self.execute_query(sql)
        data_df = data_df.drop(columns=['ID'])
        data_df = data_df.drop(columns=['收录时间'])
        data_df = data_df.drop(columns=['是否可以上传'])
        filtered_df = clean_cal(data_df, write_table=1)
        # 删除ID列
        filtered_df = filtered_df[filtered_df['发布日期'].notnull()]
        self.pf.to_mysql(filtered_df, '重庆市其他文件')
        return data_df


def main_test():
    data_dt = {
        "del_table": '专项补充收录',
        "shoulu_date": "2024.09.14",
    }
    obj = test3(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main_test()
