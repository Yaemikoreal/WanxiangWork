import json
import random
import time

import pandas as pd
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

    def delete_data(self, id):
        url = 'http://data.lawdoo.com/api/api/historydata/delHistoryDatabyIds'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'UlJ6RVo0RW9yUjBsSVpkSzBTMlhOQUx0Qm1zTFdOSXlzYnVhSE9Vb09qcHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==',}  # 改成自己的
        data = {
            "ids": f"{id}",
            # "projrctId": "fbd7f99f9649070ef0a8c9a3245e00e2"#法律法规，
            # "projrctId": "981577858f7d59da5bf2eabfc7635b71"  # 地方法规
            # "projrctId":"30417e48cf2b4a87b25022e17d7e3a45"
            "projrctId": self.projectId
        }
        jsonData = json.dumps(data, ensure_ascii=False)
        response = requests.post(url=url, headers=header, data=jsonData.encode())
        print("状态" + str(response.status_code))
        print(response.text)
        print("===="*20)

    def write_fagui(self):
        connect = pyodbc.connect(
            'Driver={SQL Server};Server=47.97.3.24,14333;Database=LawEnclosure;UID=saa;PWD=1+2-3..*Qwe!@#;'
            'charset=gbk')
        print('数据库连接成功')
        # 创建游标对象
        cursor = connect.cursor()
        sql = f"""
        SELECT
            [唯一标志],
            [法规标题],
            [全文],
            [发布部门],
            [类别],
            [发布日期],
            [效力级别],
            [实施日期],
            [发文字号],
            [时效性],
            [修订依据],
            [部分失效依据],
            [失效依据],
            [失效日期],
            [url],
            [附件]
        FROM
            [FB6.0].[dbo].[{self.table_name}]
        WHERE
            {self.where_value};
        """
        cursor.execute(sql)
        url_list = cursor.fetchall()
        # 使用列表推导式提取每个row的第一个值
        id_list = [row[0] for row in url_list]

        # data_df = pd.read_excel("")
        # id_list = ['a663af9362ba288b8e9c464973419001']
        count_num = 0
        for i in range(len(id_list)):
            count_num += 1
            time.sleep(random.uniform(0.5, 1))
            print(f"正在删除第 [{count_num}] 条数据.")
            self.delete_data(id_list[i])
        cursor.close()
        connect.close()

    def calculate(self):
        # True:法规
        if self.status:
            self.write_fagui()


if __name__ == "__main__":
    data_dt = {
        "status": True,
        "where_value": "[唯一标志] = '7930531'",
        # 法律法规 or 地方法规
        "projectId": '地方法规'
    }

    obj = get_shujuku(**data_dt)
    obj.calculate()
