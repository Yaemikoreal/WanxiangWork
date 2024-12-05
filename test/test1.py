import json
import os
from datetime import datetime
from StandardDataGet import PriceQuery
import pyodbc
import pandas as pd
import requests
from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup
import time
import random

url = 'https://hbba.sacinfo.org.cn/stdQueryList'
header = {
    "Cookie": "Hm_lvt_bc6f61eace617162b31b982f796830e6=1730340210; HMACCOUNT=C1E3DEC5C46B85EE; Hm_lpvt_bc6f61eace617162b31b982f796830e6=1730341489",
    "referer": "https://hbba.sacinfo.org.cn/stdList",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
    "origin": "https://hbba.sacinfo.org.cn",
    "content-type": "application/x-www-form-urlencoded"
}
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
}


def query_sql_BidDocument(sql):
    """
    用于执行数据库查询
    :param sql: 查询语句
    :return: 查询结果
    """
    connect = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    # 创建游标对象
    cursor = connect.cursor()
    try:
        # 执行查询
        cursor.execute(sql)
        # 获取查询结果
        results = cursor.fetchall()
        # 返回查询结果
        return results
    finally:
        # 关闭游标和连接
        cursor.close()
        connect.close()


def contains_chinese(s):
    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False


def read_filename():
    # 指定文件夹路径
    folder_path = r'E:\JXdata\每月手动数据检查\标准基础信息获取'
    # 获取文件夹下的所有文件名
    file_names = os.listdir(folder_path)
    new_file_names_lt = []
    for it in file_names:
        title = it.split(' ')
        new_title = ''
        for item in title:
            if contains_chinese(item):
                new_title += ' ' + item
        new_title = new_title.replace('.PDF', '').replace('.pdf', '').replace('\xa0', '')
        new_file_names_lt.append(new_title)
    # 处理后的列表
    new_file_names_lt = [s.strip() for s in new_file_names_lt]
    return new_file_names_lt


def post_text(filename_lt):
    new_data_lt = []
    for it in filename_lt:
        time.sleep(random.uniform(1.5, 3))
        json_data = {
            "current": "1",
            "size": "15",
            "key": f"{it}",
            "ministry": "",
            "industry": "",
            "pubdate": "",
            "date": "",
            "status": ""
        }
        try:
            response = requests.post(url=url, headers=header, data=json_data)
            if response.status_code == 200:
                msg = json.loads(response.text)
                records = msg.get('records')
                if not records:
                    print(f"数据{it}没有搜到!!!")
                    continue
                records = records[0]
                pk = records.get('pk')
                msg_dt = {
                    "标题": it,
                    "url": "https://hbba.sacinfo.org.cn/stdDetail/" + pk
                }
                print(msg_dt)
                new_data_lt.append(msg_dt)
        except Exception as e:
            print(f"数据{it}没有搜到!!!")
            continue
    data_df = pd.DataFrame(new_data_lt)
    with pd.ExcelWriter(r"E:\JXdata\每月手动数据检查\标准基础信息获取\信息.xlsx") as writer:
        data_df.to_excel(writer, startrow=0, startcol=0)
    return new_data_lt


def select_from_oa():
    sql = rf"SELECT * FROM [自收录数据].dbo.[标准库menus]"
    results = query_sql_BidDocument(sql)
    return results


def foundation_data_get():
    new_data_lt = []
    msg_df = pd.read_excel(r'E:\JXdata\每月手动数据检查\标准基础信息获取\信息.xlsx')
    for index, row in msg_df.iterrows():
        get_url = row.get('url')
        time.sleep(random.uniform(0.5, 1.5))
        response = requests.get(url=get_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 内容解析
        left_tag = soup.find('dl', attrs={'class': 'basicInfo-block basicInfo-left'})
        left_data_dt = get_data_from_tag(left_tag)
        right_tag = soup.find('dl', attrs={'class': 'basicInfo-block basicInfo-right'})
        right_data_dt = get_data_from_tag(right_tag)
        status_tag = soup.find('span', attrs={'class': 's-status label label-primary'})
        status_key = status_tag.get_text()
        merged_dict = {**left_data_dt, **right_data_dt, '标题': row.get('标题'), '标准状态': status_key}
        print(merged_dict)
        print("=====" * 20)
        new_data_lt.append(merged_dict)
    data_df = pd.DataFrame(new_data_lt)
    with pd.ExcelWriter(r"E:\JXdata\每月手动数据检查\标准基础信息获取\信息_1次处理.xlsx") as writer:
        data_df.to_excel(writer, startrow=0, startcol=0)
    return new_data_lt


def insert_data(data_df):
    connInfo = 'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=FB6.0;UID=saa;PWD=1+2-3..*Qwe!@#'
    conn = pyodbc.connect(connInfo)
    cursor = conn.cursor()
    insesql = """
        INSERT INTO [自收录数据].[dbo].[标准库_国家行业标准] (
            [唯一标志],
            [标题],
            [全文],
            [类别],
            [类别key],
            [发布部门],
            [发布日期],
            [实施日期],
            [标准状态],
            [标准状态key],
            [来源],
            [标准分类],
            [标准分类key],
            [中国标准分类号],
            [国际标准分类号],
            [标准号],
            [附件位置],
            [标准类型],
            [价格],
            [是否免费]
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

    for index, data_dt in data_df.iterrows():
        jiage = PriceQuery.get_Sell(data_dt.get('标准号'))
        print(f"价格: {jiage}")
        if jiage != "0":
            is_free = "002"
        else:
            is_free = "001"
        params_lt = (
            data_dt.get('唯一标志'),
            data_dt.get('标题'),
            data_dt.get('全文'),
            data_dt.get('类别'),
            data_dt.get('类别key'),
            data_dt.get('批准发布部门'),
            data_dt.get('发布日期'),
            data_dt.get('实施日期'),
            data_dt.get('标准状态'),
            str(data_dt.get('标准状态key')),
            data_dt.get('来源'),
            data_dt.get('标准分类'),
            str(data_dt.get('标准分类key')),
            str(data_dt.get('中国标准分类号')),
            str(data_dt.get('国际标准分类号')),
            data_dt.get('标准号'),
            data_dt.get('附件位置'),
            data_dt.get('标准类别'),
            jiage,
            is_free
        )

        try:
            cursor.execute(insesql, params_lt)
            conn.commit()
            print(f"【{data_dt.get('标题')}】 写入成功！！！")
            print("=====" * 20)
        except pyodbc.Error as ex:
            print(f"写入失败: {ex}")
            print(f"数据: {params_lt}")
            print("=====" * 20)
    cursor.close()
    conn.close()


def select_data():
    results = select_from_oa()
    menus_dt = {}
    for row in results:
        leibie = row[1]
        leibie_key = row[0]
        menus_dt[leibie] = leibie_key
    return menus_dt


def calculate_data(data_lt):
    formatted_date = datetime.now().strftime('%Y.%m.%d')
    menus_dt = select_data()
    status_dt = {
        '现行': '01',
        '废止': '04'
    }
    for it in data_lt:
        # 唯一标志(标准号+今天日期)
        it['唯一标志'] = it.get('标准号') + formatted_date
        # 类别和类别key
        leibie = it.get('标准号')[:2]
        for k, v in menus_dt.items():
            if k[:2] == leibie:
                it['类别'] = k
                it['类别key'] = v
                break
            it['类别'] = None
            it['类别key'] = None

        # 标准状态key
        status_key = it.get('标准状态')
        it['标准状态key'] = status_dt.get(status_key)
        it['标准分类'] = '行业标准'
        it['标准分类key'] = '0002'
        it['是否免费'] = '002'
        it['附件位置'] = f"/行业标准/{it.get('标准号')}.pdf"
        it['来源'] = '新版标准库'
        it['全文'] = f"""<a href="javascript:void(0)" class="" onclick="pdfck()">{it.get('标准号')} {it.get('标题')}</a>"""
    data_df = pd.DataFrame(data_lt)
    with pd.ExcelWriter(r"E:\JXdata\每月手动数据检查\标准基础信息获取\信息_2次处理.xlsx") as writer:
        data_df.to_excel(writer, startrow=0, startcol=0)
    return data_df


def get_data_from_tag(tag):
    data_dt = {}
    # 遍历 <dl> 标签下的所有 <dt> 和 <dd> 标签
    dt_tags = tag.find_all('dt', class_='basicInfo-item name')
    dd_tags = tag.find_all('dd', class_='basicInfo-item value')

    # 确保 <dt> 和 <dd> 标签的数量一致
    if len(dt_tags) == len(dd_tags):
        for dt, dd in zip(dt_tags, dd_tags):
            key = dt.get_text(strip=True)
            value = dd.get_text(strip=True)
            data_dt[key] = value
    return data_dt


if __name__ == '__main__':
    # new_file_names_lt = read_filename()
    # post_text(new_file_names_lt)


    # new_data_lt = foundation_data_get()
    # data_df = calculate_data(new_data_lt)
    data_df = pd.read_excel(r'E:\JXdata\每月手动数据检查\标准基础信息获取\信息_2次处理.xlsx')
    insert_data(data_df)