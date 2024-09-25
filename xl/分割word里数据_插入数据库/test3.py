
import pyodbc
import re
from docx import Document
import os

def save_sql_BidDocument(sql):
    '''
    用于插入数据库
    :param sql
    :return:
    '''
    connect = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=ourdata;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    # 创建游标对象
    cursor = connect.cursor()
    # sql = "INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    # cursor.executemany(sql, all_result)
    cursor.execute(sql)

    cursor.commit()
    cursor.close()
    connect.close()

def write_to_oa(read_cpntent,num):
    # cgid = '820886279'
    # name='《中华人民共和国安全生产法》（2021修订）释义'
    # tgid='805306584'
    # chapternum='1'
    # ctitle='第一章　总　　则'
    # gid='330429'abc
    sql = rf"UPDATE [ourdata].dbo.[syitemour]  SET [全文]=('{read_cpntent}') where [唯一标志] = '{num}'"
    save_sql_BidDocument(sql)
    print(sql)
    print("---插入一条了")


def read_all():
    num=838883426
    for i in range(14,119):
        wenj_path = f"D:\work\下载分割处理后的新文件\section_{i}.txt"
        with open(wenj_path, 'r', encoding='utf-8') as file:
            read_cpntent  = file.read()
            write_to_oa(read_cpntent,num)
            num += 1


if __name__ == '__main__':
    read_all()
