import re
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
import pyodbc

"""
该脚本用于匹配两张表里的标题内容并输出一张新表
"""


class WushanRelation:
    def __init__(self):
        self.server = 'localhost'
        self.database = 'test'
        self.connection_string = f'mssql+pyodbc://{self.server}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

    def get_dataframe(self, table_name):
        # 创建连接
        try:
            # 创建连接
            engine = create_engine(self.connection_string)
            # 查询 wushan_unscramble 表中的所有值
            query = text(f"SELECT * FROM {table_name}")
            # 使用 pandas 读取 SQL 查询结果
            df = pd.read_sql_query(query, engine)
            return df

        except Exception as e:
            print(f"数据库连接或查询失败: {e}")
            return None

    # 定义一个函数来提取标题中的文本
    def extract_title(self, text1):
        start_text = text1.find('《')
        end_text = text1.find('》')
        if start_text != -1 and end_text != -1:
            extracted_title = text1[start_text + 1:end_text]
            # 使用正则表达式删除括号及其内容
            extracted_title = re.sub(r'（[^)]*）', '', extracted_title).strip()
            return extracted_title
        return None

    # 定义一个函数来进行模糊匹配
    def fuzzy_match(self, title, titles):
        for t in titles:
            if title in t or t in title:
                print(f"匹配成功，标题： {title} 和 标题：{t}")
                print("-----------------------------------")
                return True
        return False

    def pipei(self, df_a, df_b):
        # 获取并格式化当前日期
        formatted_date = datetime.now().strftime('%Y.%m.%d')
        data_dt = {
            'htmgid': [],
            'gid': [],
            'name': [],
            'fdate': [],
            'htmname': [],
            'htmfdate': [],
            'htmkm': [],
            '收录日期': [],
            'tiao': [],
            'km': [],
            'subkm': []
        }
        # 遍历 DataFrame A 的“标题”列
        for index, row in df_a.iterrows():
            # 提取“标题”列中的“《》”之间的文本
            extracted_title = self.extract_title(row['标题'])
            if extracted_title is not None:
                # 与 DataFrame B 的“法规标题”列进行模糊匹配
                matched_row = df_b[df_b['法规标题'].apply(lambda x: self.fuzzy_match(extracted_title, [x]))]
                if not matched_row.empty:
                    # 规范性文件的唯一标志
                    data_dt['htmgid'].append(matched_row["唯一标志"].iloc[0])
                    # 政策解读文件的唯一标志
                    data_dt['gid'].append(row["唯一标志"])
                    # 政策解读文件的标题
                    data_dt['name'].append(row["标题"])
                    # 政策解读文件的发布日期
                    data_dt['fdate'].append(row["发布日期"])
                    # 规范性文件的标题
                    data_dt['htmname'].append(matched_row["法规标题"].iloc[0])
                    # 规范性文件的发布日期
                    data_dt['htmfdate'].append(matched_row["发布日期"].iloc[0])
                    data_dt['htmkm'].append('lar')
                    data_dt['收录日期'].append(formatted_date)
                    data_dt['tiao'].append('0')
                    data_dt['km'].append('lfbj')
                    data_dt['subkm'].append('0')
        print("匹配结果完毕！")
        return data_dt

    def to_mysql(self, df):
        # 创建连接
        try:
            engine = create_engine(self.connection_string)
        except pyodbc.OperationalError as e:
            print(f"Connection error: {e}")
            exit()
        table_name = 'test_three'
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    def caculate(self):
        wushan_unscramble_df = self.get_dataframe("wushan_unscramble")
        test_wushan_df = self.get_dataframe("test_wushan1")
        data_dt = self.pipei(wushan_unscramble_df, test_wushan_df)
        data_df = pd.DataFrame.from_dict(data_dt)
        self.to_mysql(data_df)
        print("写入完毕！")



def main():
    obj = WushanRelation()
    obj.caculate()


if __name__ == "__main__":
    main()
