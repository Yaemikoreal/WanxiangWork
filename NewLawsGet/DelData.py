import json
import requests
import pyodbc
import hashlib

"""
该方法用于进行对数据管理系统上的批量数据删除操作
传入需要删除的数据的唯一标志列表，以及对应模版值
"""
projectId_dt = {"地方法规": "981577858f7d59da5bf2eabfc7635b71",
                "法律法规": "fbd7f99f9649070ef0a8c9a3245e00e2"}
def delete_data(del_lt, projectId="法律法规"):
    comma_separated_string = ','.join(str(item) for item in del_lt)
    url = 'http://47.97.3.24:8075/api/historydata/delHistoryDatabyIds'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'Token': 'cmFlVnZKR1BoTW84b0tLZm9hTW1wWi9lWjVHMWYyaFhLQ0ZwdzV5a0FOZHVvaU94MFVTd2NGdU5ZUFZWcWZtZA==', }
    data = {
        "ids": f"{comma_separated_string}",
        "projrctId": f"{projectId_dt.get(projectId)}"
    }
    print(data)
    jsonData = json.dumps(data, ensure_ascii=False)
    response = requests.post(url=url, headers=header, data=jsonData.encode())
    print("状态" + str(response.status_code))
    print(response)


if __name__ == '__main__':
    # 需要删除的数据的唯一标志列表
    del_lt = []
    delete_data(del_lt=del_lt, projectId="地方法规")
