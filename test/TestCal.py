import pandas as pd
import query.PublicFunction as pf


def update_category(row):
    old_leib = row['类别']
    full = row['check_text']
    title = row['title']
    new_leib = pf.catagroy_select(full, title)  # 修正了拼写错误
    if old_leib != new_leib:
        print(f"[{title}] 更新类别从 [{old_leib}] 到 [{new_leib}]")
        print("====" * 20)
    return new_leib


data_df = pd.read_excel("类别问题数据.xlsx")
del data_df['id']

data_df['类别'] = data_df.apply(update_category, axis=1)
data_df.to_excel("处理后的类别问题数据.xlsx", index=False)
print(1)
