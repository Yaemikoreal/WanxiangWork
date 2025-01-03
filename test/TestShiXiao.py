import pandas as pd
import Levenshtein


def is_similar(str1, str2, threshold=0.6):
    # 计算Levenshtein距离
    distance = Levenshtein.distance(str1, str2)
    # 计算相似度
    similarity = 1 - (distance / max(len(str1), len(str2)))
    # 判断相似度是否大于等于阈值
    return similarity >= threshold


def calculate(row):
    fz1 = row.get('废止文件')
    fz2 = row.get('法器废止文件')
    fawen1 = row.get('废止文号')
    fawen2 = row.get('法器废止文号')
    if is_similar(fz1, fz2):
        print(f"标题{fz1}和{fz2}匹配")
        row['标记'] = "需要查看"
    else:
        print(f"标题{fz1}和{fz2}，差距过大，不认为为同文件")
        row['标记'] = ""
    if fawen1 == fawen2:
        row['标记'] = "需要查看"
    return row


def test():
    # Excel文件路径
    file_path = r"E:/JXdata/每月手动数据检查/明文强-废止文件梳理-20241021-分工安排（刘晓军）.xlsx"

    # 读取Excel文件，并将第二行作为列索引
    df = pd.read_excel(file_path, skiprows=1, header=0, sheet_name="有文号")
    df = df[df["负责人"] == "吉祥"]
    df["标记"] = None

    # 使用apply更新DataFrame
    df = df.apply(calculate, axis=1)

    # # 过滤出标记为"需要查看"的行
    # df1 = df[df["标记"] == "需要查看"]
    filename = 'E:/JXdata/每月手动数据检查/排查_jx.xlsx'
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, startrow=0, startcol=0, index=False)
    print(f"{filename} 写入完毕！！！")


if __name__ == '__main__':
    test()