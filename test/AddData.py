import json
import random
import time

import pandas as pd
import requests
import pyodbc


def post_sj1_difangfagui(self, query_result):
    url = 'http://data.lawdoo.com/api/api/trends/addEmployData'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'Token': 'bVlWTk53SlVkUEZXM3hnWnhjMVp4QlBEeEd4dzY0Rm8yZEZGeUxTTTZ4eHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
    data = {
        'data': {
            "identifying": query_result[0],
            "title": query_result[1],
            "original_text": query_result[2],
            "processing_text": query_result[2],
            "check_text": query_result[2],
            "file_url": "",
            "statistics_type": "2",  # 1是待校验   2是待打包  3是已打包
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
        "projectId": "981577858f7d59da5bf2eabfc7635b71"
    }
    jsonData = json.dumps(data, ensure_ascii=False)
    response = requests.post(url=url, headers=header, data=jsonData.encode())
    print(response.text)
    print("状态" + str(response.status_code), "写入成功", data)


def calculate_data(value):
    if pd.isna(value):  # 检查是否为 NaN 或 None
        return ""
    elif isinstance(value, int):  # 检查是否为整数
        return f"{value:02d}"  # 格式化为两位数的字符串
    else:
        return str(value)  # 其他情况直接转换为字符串


def post_sj1_fagui(row):
    row = row.apply(calculate_data)
    url = 'http://data.lawdoo.com/api/api/trends/addEmployData'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'Token': 'UlJ6RVo0RW9yUjBsSVpkSzBTMlhOQUx0Qm1zTFdOSXlzYnVhSE9Vb09qcHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
    data = {
        'data': {
            "identifying": str(row.get('identifying')),
            "title": str(row.get('title')),
            "original_text": str(row.get('original_text')),
            "processing_text": str(row.get('processing_text')),
            "check_text": str(row.get('check_text')),
            "file_url": "",
            "statistics_type": "2",
            "source": str(row.get('source')),
            "发布部门": str(row.get('发布部门')),
            "类别": str(row.get('类别')),
            "发布日期": str(row.get('发布日期')),
            "效力级别": str(row.get('效力级别')),
            "实施日期": str(row.get('实施日期')),
            "发文字号": str(row.get('发文字号')),
            "时效性": str(row.get('时效性')),
            "修订依据": str(row.get('修订依据')),
            "部分失效依据": str(row.get('部分失效依据')),
            "失效依据": str(row.get('失效依据')),
            "失效日期": str(row.get('失效日期')),
        },
        # TODO 写入之前注意传入的模版
        "projectId": "981577858f7d59da5bf2eabfc7635b71"  # 地方法规
        # "projectId":""fbd7f99f9649070ef0a8c9a3245e00e2""      # 法律法规
    }
    # print(data)
    jsonData = json.dumps(data, ensure_ascii=False)
    try:
        response = requests.post(url=url, headers=header, data=jsonData.encode(), timeout=10)
        if response.status_code == 200:
            print(f"[{row.get('title')}][{row.get('类别')}]连接写入成功!")
    except Exception as e:
        print(f"错误:[{row.get('title')}][{row.get('类别')}]写入失败!!!!")
        print(e)
    print("====" * 30)


def calculate():
    data_df = pd.read_excel("处理后的类别问题数据.xlsx")
    for index, row in data_df.iterrows():
        post_sj1_fagui(row)
        time.sleep(random.uniform(1.5, 2))


if __name__ == '__main__':
    calculate()
