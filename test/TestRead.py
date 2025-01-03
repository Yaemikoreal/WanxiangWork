import pandas as pd
import pyodbc


# 建立数据库连接
try:
    connect = pyodbc.connect(
        'Driver={SQL Server};Server=47.97.3.24,14333;Database=LawEnclosure;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    print("连接成功！")
except Exception as e:
    print(f"连接失败: {e}")
    exit()

# 定义SQL查询语句
query = f"""
        SELECT 
            *
        FROM 
            [EmployData].[dbo].[地方法规]
        WHERE 
            [create_by] = '888b0c09f5a34215a6d76ded2690da86'
            AND LEN([类别]) > 9;
        """

# 使用pandas的read_sql函数读取数据并生成DataFrame
try:
    df = pd.read_sql(query, connect)
    print("数据读取成功！")
    print(df.head())  # 显示前5行数据
    df.to_excel('类别问题数据.xlsx', index=False)
except Exception as e:
    print(f"读取数据失败: {e}")

# 关闭数据库连接
connect.close()
print("连接已关闭。")