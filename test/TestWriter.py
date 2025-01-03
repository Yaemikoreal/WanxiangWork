import pyodbc
from bs4 import BeautifulSoup
from datetime import datetime
from sqlalchemy import create_engine
from query import PublicFunction
import pandas as pd
import json
import random
import time
import requests
import pyodbc
class get_shujuku(object):

    def __init__(self, **kwargs):
        self.va_dt = {
            "法律法规": {"table_name": 'fb_新版中央法规_chl', "projectId": '法律法规'},
            "地方法规": {"table_name": 'fb_新版地方法规_lar', "projectId": '地方法规'}
        }
        # 法规模版
        self.projectId_dt = {
            "地方法规": "981577858f7d59da5bf2eabfc7635b71",
            "法律法规": "fbd7f99f9649070ef0a8c9a3245e00e2"
        }
        # 需要写入的法规模版地址
        self.mb = kwargs.get('projectId')
        self.projectId = self.projectId_dt.get(self.mb)
        # status,ture为法规，False为解读文件
        self.status = kwargs.get('status')
        # 需要写入的表名
        self.table_name = self.va_dt.get(self.mb).get('table_name')
        # where条件语句
        self.where_value = kwargs.get('where_value')

    def post_sj1_fagui(self, row):
        print(f"正在写入文章:  {row['法规标题']}")
        print(f"注意: 正在往 [{self.mb}] 模版中写入数据!!!")
        url = 'http://47.97.3.24:8075/api/trends/addEmployData'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'UlJ6RVo0RW9yUjBsSVpkSzBTMlhOQUx0Qm1zTFdOSXlzYnVhSE9Vb09qcHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
        data = {
            'data': {
                "identifying": row['唯一标志'],
                "title": row['法规标题'],
                "original_text": row['全文'],
                "processing_text": row['全文'],
                "check_text": row['全文'],
                "file_url": "",
                "statistics_type": "2",
                "source": row['url'],
                "发布部门": row['发布部门'],
                "类别": row['类别'],
                "发布日期": row['发布日期'],
                "效力级别": row['效力级别'],
                "实施日期": row['实施日期'],
                "发文字号": row['发文字号'],
                "时效性": row['时效性'],
                "修订依据": '',
                "部分失效依据": '',
                "失效依据": '',
                "失效日期": '',
            },
            # TODO 写入之前注意传入的模版
            "projectId": f"{self.projectId}"
            # "projectId":""fbd7f99f9649070ef0a8c9a3245e00e2""      # 法律法规
        }
        # print(data)
        jsonData = json.dumps(data, ensure_ascii=False)
        try_num = 5
        while True:
            try:
                response = requests.post(url=url, headers=header, data=jsonData.encode(), timeout=10)
                if response.status_code == 200:
                    print(f"连接写入成功!")
                    print("===" * 30)
                    break
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(random.uniform(2, 2.5))
                if try_num == 0:
                    print(f"重试次数用尽(3),跳过...")
                    break
                try_num -= 1
                print("正在进行重试...")

    def post_sj1_jiedu(self, row):
        url = 'http://47.97.3.24:8075/api/trends/addEmployData'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'UlJ6RVo0RW9yUjBsSVpkSzBTMlhOQUx0Qm1zTFdOSXlzYnVhSE9Vb09qcHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
        data = {
            'data': {
                "identifying": row['唯一标志'],
                "title": row['标题'],
                "original_text": row['全文'],
                # "source": '',
                "发布部门": row['发布部门'],
                "类别": row['类别'],
                "发布日期": row['发布日期'],
                "source": row['来源']
            },
            "projectId": "a3ea8f1619bc8435285e7ecfd71ed2cc"
        }
        jsonData = json.dumps(data, ensure_ascii=False)
        try_num = 5
        # while True:
        #     try:
        print(f"正在写入: {row['标题']}")
        response = requests.post(url=url, headers=header, data=jsonData.encode(), timeout=20)
        if response.status_code == 200:
            print(f"连接写入成功!")
            print("===" * 30)
        else:
            print("失败")
            # break
            # except Exception as e:
            #     print(f"错误: {e}")
            #     time.sleep(random.uniform(2, 2.5))
            #     if try_num == 0:
            #         print(f"重试次数用尽(3),跳过...")
            #         break
            #     try_num -= 1
            #     print("正在进行重试...")

    def write_fagui(self):
        data_df = self.from_mysql('天津新疆')
        count_num = 0
        for index, row in data_df.iterrows():
            count_num += 1
            if row.get('法规标题') == "甘肃省市场监督管理局关于印发甘肃省  市场监督管理行政处罚裁量权  基准（一）的通知":
                time.sleep(random.uniform(0.5, 1))
                print(f"正在写入第 [{count_num}] 条数据.")
                self.post_sj1_fagui(row)

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

    def write_jiedu(self):
        data_df = self.from_mysql('天津新疆-政策解读')
        count_num = 0
        for index, row in data_df.iterrows():
            count_num += 1
            # if row.get('法规标题') == "关于印发《新疆维吾尔自治区新疆生产建设兵团市场监督管理行政处罚裁量权适用规定》《新疆维吾尔自治区新疆生产建设兵团市场监督管理行政处罚裁量基准（2024年）》的通知":
            time.sleep(random.uniform(0.5, 1))
            print(f"正在写入第 [{count_num}] 条数据.")
            self.post_sj1_jiedu(row)

    def calculate(self):
        # True:法规 ,  False:解读
        if self.status:
            self.write_fagui()
        else:
            self.write_jiedu()


if __name__ == "__main__":
    data_dt = {
        "status": False,
        "where_value": "[收录日期] = '20241112'",
        # 法律法规 or 地方法规
        "projectId": '地方法规'
    }

    obj = get_shujuku(**data_dt)
    obj.calculate()
