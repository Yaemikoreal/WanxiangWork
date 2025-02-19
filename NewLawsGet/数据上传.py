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
        #
        self.title_not_lt = ['同志任免职的通知', '职务任免的通知', '工作职务的通知', '同志退休的通知',
                             '同志挂任职务的通知', '同志挂职的通知', '任职的通知', '同志正式任职的通知',
                             '同志试用期满正式任用的通知', '同志职级任职的通知', '同志免职退休的通知',
                             '轮岗调整的通知', '同志免职通知', '同志岗位聘用的通知', '领导分工调整的通知',
                             '领导班子工作分工的通知', '工作人员职务的通知', '同志职务聘任的通知', '免职的通知',
                             '任职资格的批复',
                             '任职资格核准的批复', '同志职级晋升的通知', '同志职级套转的通知',
                             '同志职级晋升和免职的通知', '同志任职的决定', '同志提前退休的通知', '试用期满任职的通知',
                             '组成人员的通知', '挂职服务锻炼的通知', '同志到龄退休的通知', '同志试用期转正的通知',
                             '同志职务调整的通知', '同志晋升职级的通知', '同志聘任的通知',
                             '调整领导工作分工的通知', '指挥部成员的通知', '同志确定职级的通知', '同志任(聘)职的通知',
                             '同志职务职级调整的通知', '同志主持工作的通知', '同志职务的通知', '领导分工的通知',
                             '指挥部组成人员的通知', '同志免职(退休)的通知',
                             '职务职级任免的通知', '工作分工调整的通知', '负责人调整的通知', '调整工作领导小组的通知',
                             '任职资格的通知', '职级的通知', '聘任的批复', '同志工作安排的通知', '确定职级的通知',
                             '离任的通知', '同志轮岗交流的通知', '同志转正的通知', '解聘的通知', '挂职的通知',
                             '调整河长的通知', '选举情况的通报', '同志分工的通知']

    def judge_title(self, title):
        for it in self.title_not_lt:
            if it in title:
                print(f"{title} 属于人事任免内容!")
                return False
        print(f"{title} 不在人事任免内容!")
        return True

    def post_sj1_fagui(self, query_result):
        # if query_result[0] not in ["7930531", "7931623"]:
        #     print(f"该数据不需要再上传 [{query_result[1]}]")
        #     print("===" * 30)
        #     return
        print(f"正在写入文章:  {query_result[1]}")
        print(f"注意: 正在往 [{self.mb}] 模版中写入数据!!!")
        url = 'http://data.lawdoo.com/api/api/trends/addEmployData'
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
                "source": query_result[14],
                "发布部门": query_result[3],
                "类别": query_result[4],
                "发布日期": query_result[5],
                "效力级别": query_result[6],
                "实施日期": query_result[7],
                "发文字号": query_result[8],
                "时效性": query_result[9],
                "修订依据": query_result[10],
                "部分失效依据": query_result[11],
                "失效依据": query_result[12],
                "失效日期": query_result[13],
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
        count_num = 0
        for i in range(len(url_list)):
            count_num += 1
            title = url_list[i][1]
            if self.judge_title(title):
                time.sleep(random.uniform(0.5, 1))
                print(f"正在写入第 [{count_num}] 条数据.")
                self.post_sj1_fagui(url_list[i])
            else:
                # TODO 补充逻辑：处理人事任免内容的上传.
                pass
        cursor.close()
        connect.close()

    def write_jiedu(self):
        connect = pyodbc.connect(
            'Driver={SQL Server};Server=47.97.3.24,14333;Database=LawEnclosure;UID=saa;PWD=1+2-3..*Qwe!@#;'
            'charset=gbk')
        print('数据库连接成功')
        # 创建游标对象
        cursor = connect.cursor()
        sql = """
            SELECT 
                [唯一标志],
                [标题],
                [全文],
                [发布部门],
                [类别],
                [发布日期],
                [收录日期]
            FROM 
                [FB6.0].[dbo].[fb_新版中央法规_chl]
            WHERE 
                [收录日期] LIKE '2024.09.17' 
                OR [收录日期] LIKE '2024.09.18';
        """
        cursor.execute(sql)
        url_list = cursor.fetchall()
        for i in range(len(url_list)):
            # print(url_list[i])
            time.sleep(2)
            self.post_sj1_jiedu(url_list[i])
        cursor.close()
        connect.close()

    def calculate(self):
        # True:法规 ,  False:解读
        if self.status:
            self.write_fagui()
        else:
            self.write_jiedu()


if __name__ == "__main__":
    data_dt = {
        "status": True,
        "where_value": "[收录日期] = '20250103'",
        # 法律法规 or 地方法规
        "projectId": '地方法规'
    }

    obj = get_shujuku(**data_dt)
    obj.calculate()
