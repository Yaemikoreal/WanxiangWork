import os
import pandas as pd
import pyodbc
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from query import PublicFunction as pf

es_client = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)
connInfo = 'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=FB6.0;UID=saa;PWD=1+2-3..*Qwe!@#'
conn = pyodbc.connect(connInfo)
cursor = conn.cursor()


def check_article_exists(title, index_name='chl'):
    """
    检查 Elasticsearch 中是否存在给定标题的文章。

    参数:
    title (str): 文章标题。
    index_name (str): Elasticsearch 索引名称，默认为 'lar'。

    返回:
    bool: 如果文章不存在返回 True，否则返回 False。
    """
    query_body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "标题": {
                                "query": title,
                                "slop": 0,
                                "zero_terms_query": "NONE",
                                "boost": 1.0
                            }
                        }
                    }
                ]
            }
        },
        "from": 0,
        "size": 10
    }
    response = es_client.search(index=index_name, body=query_body)
    if int(response['hits']['total']) == 0:
        print(f'{index_name} 不存在该文章!!  {title}')
        return False, None
    else:
        data_lt = response['hits']['hits']
        print(f'{index_name} 已经存在该文章!!  {title}，共有【{len(data_lt)}】个搜索结果。')
        return True, data_lt


def select_sql():
    # 定义查询语句
    query_sql = f"""
    SELECT 
        法规标题, 
        发文字号, 
        类别, 
        发布日期, 
        实施日期, 
        发布部门, 
        时效性, 
        效力级别, 
        法宝引证码, 
        唯一标志, 
        收录日期,
        url
    FROM 
        fb_新版中央法规_chl
    WHERE 
        收录日期 = '20241113' 
    """
    # 执行查询
    cursor.execute(query_sql)
    # 获取查询结果
    results = cursor.fetchall()
    # 将 pyodbc.Row 对象转换为元组
    results = [tuple(row) for row in results]
    # 定义列名
    columns_lt = [
        "法规标题",
        "发文字号",
        "类别",
        "发布日期",
        "实施日期",
        "发布部门",
        "时效性",
        "效力级别",
        "法宝引证码",
        "唯一标志",
        "收录日期",
        "url"
    ]
    # 将列表转换为 DataFrame
    data_df = pd.DataFrame(results, columns=columns_lt)
    return data_df


def analysis(fq_msg, fb_row,it_id,row_id):
    if it_id == row_id:
        return True
    fb_fawen = fb_row.get('发文字号')
    fq_fawen = fq_msg.get('发文字号')
    if fb_fawen and fq_fawen:
        fb_fawen = fb_fawen.replace('[', '').replace(']', '').replace('〔', '').replace('〕', '')
        fq_fawen = fq_fawen.replace('[', '').replace(']', '').replace('〔', '').replace('〕', '')
    if fb_fawen == fq_fawen:
        return True
    fb_fb_date = fb_row.get('发布日期').replace('.', '')
    fq_fb_date = fq_msg.get('发布日期').replace('.', '')
    fb_ss_date = fb_row.get('实施日期').replace('.', '')
    fq_ss_date = fq_msg.get('实施日期').replace('.', '')
    if fb_ss_date == fq_ss_date and fq_fb_date == fb_fb_date:
        return True
    return False


def calculate():
    new_data_lt = []
    data_df = select_sql()
    for index, row in data_df.iterrows():
        is_write = True
        title = row.get('法规标题')
        status, data_lt = check_article_exists(title)
        if status:
            for it in data_lt:
                it_id = it.get('_id')
                row_id = row.get('唯一标志')
                any_msg = it.get('_source')
                if analysis(any_msg, row,it_id,row_id):
                    print("该数据不需要写入")
                    is_write = False
                    break
            if is_write is True:
                # TODO 经过这个循环的数据都是要写入的row
                row_dt = row.to_dict()
                new_data_lt.append(row_dt)
                print(f"搜索到结果，但是不存在{row}")
                print("===="*20)
        else:
            row_dt = row.to_dict()
            new_data_lt.append(row_dt)
            print(f"没有这条数据 {row}")
            print("====" * 20)
    new_data_df = pd.DataFrame(new_data_lt)

    df_unique = new_data_df.drop_duplicates(subset='发文字号')
    df_unique = df_unique.drop_duplicates(subset='法宝引证码')
    with pd.ExcelWriter('排查_重复数据值_需要写入.xlsx') as writer:
        df_unique.to_excel(writer, startrow=0, startcol=0, index=False)
    print(1)


def cal(it):
    print(1)
    print(it)

def test():
    data_df = pd.read_excel('排查_重复数据值_排查结果.xlsx')

    data_df["url"] = data_df["url"].apply(cal)
    print(1)

if __name__ == '__main__':
    test()
    # calculate()
    # check_article_exists('中国银保监会关于公布2019年度系统公务员录用考试入围体检和考察环节人员名单的通知')
