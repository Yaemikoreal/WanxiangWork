import pandas as pd
import pyodbc


def insertsql():
    # 创建游标对象
    data1=pd.read_excel(r'C:\Users\admin\Desktop\Files\要入库的关联数据.xlsx')
    # data1 = pd.read_excel(r'C:\Users\NINGMEI\Desktop\专项补充收录单条数据________手动收录.xlsx', sheet_name='专项补充收录单条数据________手动收录')
    for z in range(len(data1['唯一标志'])):
        # print(rf"('{data1['法规id'][z]}','{data1['唯一标志'][z]}','0','lfbj','0','{data1['标题'][z]}','{data1['发布日期'][z]}','{data1['对应法规'][z]}','{data1['对应日期'][z]}','lar')")
        connect = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=ourdata;UID=saa;PWD=1+2-3..*Qwe!@#;'
            'charset=gbk')
        print('数据库连接成功')
        cursor = connect.cursor()
        # if data1['类型'][z]=='chl':
        #     sql = rf"INSERT INTO [ourdata].[dbo].[alftwotitleour]([htmgid],[gid],[tiao],[km],[subkm],[name],[fdate],[htmname],[htmfdate],[htmkm],[收录日期]) VALUES ('{data1['法规id'][z]}','{data1['唯一标志'][z]}','0','lfbj','0','{data1['标题'][z]}','{data1['发布日期'][z]}','{data1['对应法规'][z]}','{data1['对应日期'][z]}','chl','20241015')"
        # else:
        sql = rf"INSERT INTO [ourdata].[dbo].[alftwotitleour]([htmgid],[gid],[tiao],[km],[subkm],[name],[fdate],[htmname],[htmfdate],[htmkm],[收录日期]) VALUES ('{data1['法规id'][z]}','{data1['唯一标志'][z]}','0','lfbj','0','{data1['标题'][z]}','{data1['发布日期'][z]}','{data1['对应法规'][z]}','{data1['对应日期'][z]}','lar','JX20241206')"
        # print(sql)
        cursor.execute(sql)
        cursor.commit()
        print("链接插入success")
        cursor.close()
        connect.close()

if __name__ == '__main__':
    insertsql()