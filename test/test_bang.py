import random

import numpy as np
import pandas as pd

conent_df = pd.read_excel(r"E:\return1\采购订单.xls")
data_dt = {}


def calculate_conent_df(row):
    xihao = row.get('采购规格型号')
    jiage = row.get('单位价格')
    if xihao not in data_dt:
        data_dt[xihao] = [jiage]
    else:
        if jiage != 0 and jiage not in data_dt[xihao]:
            data_dt[xihao].append(jiage)


# # 提取A列和B列，并转换成字典
# dict_ab = df.set_index('外协规格型号')['单位价格'].to_dict()
conent_df.apply(calculate_conent_df, axis=1)
read_df = pd.read_excel(r"E:\return1\QHFC-8PC-C清单模板_2024.10.29.xlsx")
# 删除 '型号规格' 列为空的行
read_df = read_df.dropna(subset=['分类代码'])


def row_cal(row):
    guige = row.get('型号规格')
    jiage = row.get('参考价格（元）')
    new_jiage_lt = data_dt.get(guige)
    if not new_jiage_lt:
        new_jiage_lt = data_dt.get(f'{guige}（W）')

    if np.isnan(jiage):
        if new_jiage_lt:
            random_value = random.choice(new_jiage_lt)
            row['参考价格（元）'] = random_value
        else:
            row['参考价格（元）'] = 0
    else:
        if new_jiage_lt:
            random_value = random.choice(new_jiage_lt)
            row['参考价格（元）'] = jiage + random_value
        else:
            row['参考价格（元）'] = jiage
    row['参考价格（元）'] = round(row['参考价格（元）'], 2)
    return row


new_read_df = read_df.apply(row_cal, axis=1)
filename = r"E:\return1\QHFC-8PC-C清单模板_2024.10.29_real.xlsx"
with pd.ExcelWriter(filename) as writer:
    new_read_df.to_excel(writer, startrow=0, startcol=0, index=False)
print(f"{filename} 写入完毕！！！")
