import pandas as pd
from sqlalchemy import create_engine, text
from botpy import logging

_log = logging.get_logger()


def fetch_title_data():
    # 数据库连接信息
    server = 'localhost'
    database = 'test'
    table_name = 'chlour'
    # Integrated Security=True启用Windows身份验证
    connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    # 创建连接
    try:
        engine = create_engine(connection_string)
        # 构建查询语句
        query = text(f"SELECT * FROM {table_name}")
        # 执行查询并获取所有行
        with engine.connect() as connection:
            result = connection.execute(query)
            # 将结果转换为DataFrame
            df = pd.DataFrame(result.fetchall())
            df.columns = result.keys()
        return df

    except Exception as e:
        _log.info(f"数据库连接或查询失败: {e}")
        return None


def update_full_text(df):
    # 遍历DataFrame并对“全文”列进行修改
    for index, row in df.iterrows():
        new_text = modify_text(row['全文'])
        df.at[index, '全文'] = new_text
    return df


def modify_text(text):
    # 在这里实现对文本的修改逻辑
    # 例如：删除所有的`<!-- 附件获取 -->`注释
    return text.replace('<!-- 附件获取 -->', '')


df = fetch_title_data()
update_full_text(df)
