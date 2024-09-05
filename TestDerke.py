from CQWushan import WushanStandardizedDocuments
from bs4 import BeautifulSoup
import hashlib
import pandas as pd
from sqlalchemy import create_engine
import pyodbc

"""
该脚本用于手工验证并写入库
"""

def to_mysql(df):
    # 数据库连接信息
    server = 'localhost'
    database = 'test'
    # Integrated Security=True启用Windows身份验证
    connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    # 创建连接
    try:
        engine = create_engine(connection_string)
    except pyodbc.OperationalError as e:
        print(f"Connection error: {e}")
        exit()
    table_name = 'chlour'
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)


obj = WushanStandardizedDocuments.WushanStandardizedDocuments()
# 读取HTML文件
with open('test.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

# 使用BeautifulSoup解析HTML文档
soup_ture = BeautifulSoup(html_content, 'html.parser')
soup_ture = obj.soup_cal(soup_ture)
soup_ture = obj.remove_nbsp(soup_ture)
# print(soup_ture)
soup_text = str(soup_ture)

title = "新疆维吾尔自治区农业农村厅中共新疆维吾尔自治区委员会农村工作领导小组办公室新疆维吾尔自治区发展和改革委员会新疆维吾尔自治区财政厅新疆维吾尔自治区自然资源厅新疆维吾尔自治区水利厅新疆维吾尔自治区人民政府国有资产监督管理委员会新疆维吾尔自治区市场监督管理局新疆维吾尔自治区地方金融管理局新疆维吾尔自治区林业和草原局新疆维吾尔自治区供销合作社联合社关于印发《新疆维吾尔自治区农村产权流转交易管理办法(试行)》的通知"
date_a = '2024.03.27'
fawen = '新农政改规〔2024〕1号'
bumen = {
    '人力资源社会保障部': "6;602;60236",
    '新疆维吾尔自治区其他机构': "8;829;82903"
}
xiaoli = {
    '部门规范性文件': 'XE0302',
    '地方规范性文件': 'XP08'
}
leibie = {
    '社会福利与社会保障': '015;01505',
    '机关工作综合规定': '00;00301'
}
shixiao = '01'


def get_md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


text1 = title + date_a
md5_value = get_md5(text1)
print(md5_value)

data_dt = {
    "唯一标志": [md5_value],
    "法规标题": [title],
    "全文": [soup_text],
    "发布日期": [date_a],
    "发文字号": [fawen],
    "发布部门": [bumen['新疆维吾尔自治区其他机构']],
    "效力级别": [xiaoli['地方规范性文件']],
    "时效性": [shixiao],
    "类别": [leibie['机关工作综合规定']],
    "实施日期": ['2024.05.08']
}
df = pd.DataFrame.from_dict(data_dt)
to_mysql(df)
print("写入成功！")
