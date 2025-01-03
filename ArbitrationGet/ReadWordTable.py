import time

from docx import Document
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError


def read_table_from_word(file_path):
    # 加载Word文档
    doc = Document(file_path)

    # 初始化一个空列表来存储所有表格的数据
    all_tables_data = []

    # 遍历文档中的每个表格
    for table in doc.tables:
        # 初始化一个空列表来存储当前表格的数据
        table_data = []

        # 遍历表格中的每一行
        for row in table.rows:
            # 初始化一个空列表来存储当前行的数据
            row_data = []

            # 遍历行中的每个单元格
            for cell in row.cells:
                # 添加单元格内容到当前行的数据列表中
                row_data.append(cell.text)

            # 添加当前行的数据到当前表格的数据列表中
            table_data.append(row_data)

        # 将当前表格的数据添加到所有表格的数据列表中
        all_tables_data.append(table_data)

    # 将第一个表格的数据转换为DataFrame（如果有多个表格，可以根据需要选择）
    if all_tables_data:
        # 分离表头和数据
        headers = all_tables_data[0][0]
        data = all_tables_data[0][1:]

        # 创建DataFrame并设置列索引
        df = pd.DataFrame(data, columns=headers)
    else:
        df = pd.DataFrame()  # 如果没有表格，则返回空DataFrame

    return df


def execute_sql(sql, host="47.97.3.24:53306", user="root",
                password="99xZZPBpmceAzpuL^AHuhVome50iglKP%e*2V!RJY$To3VR15#1NT#JhoNgROjO3", database="zcxcx"):
    """
    执行任意SQL语句

    :param host: 数据库主机地址
    :param user: 数据库用户名
    :param password: 数据库密码
    :param database: 数据库名称
    :param sql: 要执行的SQL语句
    """
    try:
        # 创建数据库引擎
        engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

        # 创建会话
        Session = sessionmaker(bind=engine)
        session = Session()

        # 执行SQL语句
        result = session.execute(text(sql))

        # 提交事务
        session.commit()

        # 如果是查询语句，返回结果
        if sql.strip().upper().startswith('SELECT'):
            return result.fetchall()

        print("SQL语句已成功执行")

    except SQLAlchemyError as e:
        session.rollback()
        print(f"执行SQL语句时发生错误: {e}")
        print(f"sql : {sql}")

    finally:
        # 关闭会话
        session.close()


def calculate():
    # 示例用法
    file_path = '仲裁员名单.docx'
    data_df = read_table_from_word(file_path)
    data_df['序号'] = data_df['序号'].replace('\xa0', '')
    data_df['专长'] = data_df['专长'].replace('\xa0', '')
    data_df = data_df[data_df['序号'] != '因回避等需要特殊支出情形，由仲裁委指定担任首裁的仲裁员名单']

    for index, row in data_df.iterrows():
        time.sleep(0.3)
        sql_query = f"""
           INSERT INTO `zcxcx`.`arbitrator_name_info` ( `id`,`name`, `excel`, `address`, `job_type`, `is_del`, `create_by`, `create_time`)
               VALUES
                   ( '{int(row.get("序号"))}','{row.get("姓名")}', '{row.get("专长")}', '{row.get("所在地区")}', '1', '0', 'jx', '2024-11-15 10:45:48');
            """
        execute_sql(sql_query)
        print("===="*20)


if __name__ == '__main__':
    calculate()
