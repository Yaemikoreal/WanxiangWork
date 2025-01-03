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

    def delete_data_try(self):
        url = 'http://data.lawdoo.com/api/api/historydata/delHistoryDatabyIds'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'bVlWTk53SlVkUEZXM3hnWnhjMVp4QlBEeEd4dzY0Rm8yZEZGeUxTTTZ4eHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }  # 改成自己的
        data = {
            "ids": "a663af9362ba288b8e9c464973419001",
            "projrctId": "981577858f7d59da5bf2eabfc7635b71"  # 地方法规
        }
        # print(data)
        jsonData = json.dumps(data, ensure_ascii=False)
        response = requests.post(url=url, headers=header, data=jsonData.encode())
        print("状态" + str(response.status_code))
        print(response.text)
    def delete_data(self, id):
        url = 'http://data.lawdoo.com/api/api/historydata/delHistoryDatabyIds'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'UlJ6RVo0RW9yUjBsSVpkSzBTMlhOQUx0Qm1zTFdOSXlzYnVhSE9Vb09qcHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }  # 改成自己的
        data = {
            "ids": f"{id}",
            "projrctId": "981577858f7d59da5bf2eabfc7635b71"
        }
        jsonData = json.dumps(data, ensure_ascii=False)
        response = requests.post(url=url, headers=header, data=jsonData.encode())
        print("状态" + str(response.status_code))
        print(response.text)
        print("====" * 20)

    def write_fagui(self):

        data_df = pd.read_excel("处理后的类别问题数据.xlsx")
        id_list = data_df['identifying'].tolist()
        # id_list = ['a663af9362ba288b8e9c464973419001']
        count_num = 0
        for i in range(len(id_list)):
            count_num += 1
            time.sleep(random.uniform(0.5, 1))
            print(f"正在删除第 [{count_num}] 条数据.")
            self.delete_data(str(id_list[i]))

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
