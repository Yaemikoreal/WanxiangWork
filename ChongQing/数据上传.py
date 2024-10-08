import json
import random
import time
import requests
import pyodbc


class get_shujuku(object):

    def __init__(self, **kwargs):
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
        self.table_name = kwargs.get('table_name')
        # where条件语句
        self.where_value = kwargs.get('where_value')

    def post_sj1_fagui(self, query_result):
        print(f"正在写入文章:  {query_result[1]}")
        print(f"注意: 正在往 [{self.mb}] 模版中写入数据!!!")
        url = 'http://47.97.3.24:8075/api/trends/addEmployData'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'UlJ6RVo0RW9yUjBsSVpkSzBTMlhOQUx0Qm1zTFdOSXlzYnVhSE9Vb09qcHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
        data = {
            'data': {
                "identifying": query_result[0],
                "title": query_result[1],
                "original_text": query_result[2],
                "processing_text": query_result[2],
                "check_text": query_result[2],
                "file_url": "",
                "statistics_type": "2",
                "发布部门": query_result[3],
                "类别": query_result[4],
                "发布日期": query_result[5],
                "效力级别": query_result[6],
                "实施日期": query_result[7],
                "发文字号": query_result[8],
                "时效性": query_result[9],
                "来源": query_result[11]
            },
            # TODO 写入之前注意传入的模版
            "projectId": f"{self.projectId}"
            # "projectId":""fbd7f99f9649070ef0a8c9a3245e00e2""      # 法律法规
        }
        print(data)
        jsonData = json.dumps(data, ensure_ascii=False)
        response = requests.post(url=url, headers=header, data=jsonData.encode())
        print(f"连接状态: {str(response.status_code)}")
        print("===" * 30)

    def post_sj1_jiedu(self, query_result):
        url = 'http://47.97.3.24:8075/api/trends/addEmployData'
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
            'Token': 'cmFlVnZKR1BoTW84b0tLZm9hTW1wWi9lWjVHMWYyaFhLQ0ZwdzV5a0FOZHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
        data = {
            'data': {
                "identifying": query_result[0],
                "title": query_result[1],
                "original_text": query_result[2],
                "source": '',
                "发布部门": query_result[3],
                "类别": query_result[4],
                "发布日期": query_result[5]
            },
            "projectId": "a3ea8f1619bc8435285e7ecfd71ed2cc"
        }
        print(data)
        jsonData = json.dumps(data, ensure_ascii=False)
        response = requests.post(url=url, headers=header, data=jsonData.encode())
        print("状态" + str(response.status_code))
        print(response)

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
            [附件],
            [来源]
        FROM 
            [自收录数据].[dbo].[{self.table_name}]
        WHERE 
            {self.where_value};
        """
        cursor.execute(sql)
        url_list = cursor.fetchall()
        count_num = 0
        for i in range(len(url_list)):
            count_num += 1
            time.sleep(random.uniform(1, 2))
            print(f"正在写入第 [{count_num}] 条数据.")
            self.post_sj1_fagui(url_list[i])
        cursor.close()
        connect.close()

    def calculate(self):
        # True:法规
        if self.status:
            self.write_fagui()


if __name__ == "__main__":
    data_dt = {
        "status": True,
        "table_name": '专项补充收录',
        "where_value": "[收录时间] = 'JX2024.10.08'",
        "projectId": '地方法规'
    }

    obj = get_shujuku(**data_dt)
    obj.calculate()
