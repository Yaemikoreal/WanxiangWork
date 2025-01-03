import math
import os
import pandas as pd
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from query.PublicFunction import load_config


def calculate():
    new_data_lt = []
    data_df = pd.read_excel(r'排查_81_结果_t1.xlsx')
    for index, row in data_df.iterrows():
        fb_lt = row.get('发布部门')
        fb_title = row.get('法宝标题')
        fq_title = row.get('标题')
        if not isinstance(fb_lt, str) and math.isnan(fb_lt):
            print(f"排查错误1: 法宝标题:[{fb_title}], 法器标题:[{fq_title}]")
            data_dt = row.to_dict()
            new_data_lt.append(data_dt)
            print(row)
            print("====" * 30)
            continue
        if '60322' not in fb_lt:
            print(f"排查错误2: 法宝标题:[{fb_title}], 法器标题:[{fq_title}]")
            data_dt = row.to_dict()
            new_data_lt.append(data_dt)
            print(row)
            print("===="*30)
        else:
            print(f"[{fq_title}] 在指定发布部门下!")
            print("====" * 30)
    new_data_df = pd.DataFrame(new_data_lt)
    # 指定列的顺序
    new_order = ['法宝标题', '标题', '发文字号', 'lib', '发布部门', '效力级别', '时效性', '类别', 'order']
    new_data_df = new_data_df[new_order]
    with pd.ExcelWriter('排查_81_结果_最终_test.xlsx') as writer:
        new_data_df.to_excel(writer, startrow=0, startcol=0, index=False)
    print(1)
    pass


if __name__ == '__main__':
    calculate()
