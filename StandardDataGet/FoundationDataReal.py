from datetime import datetime
import pyodbc
from StandardDataGet import PriceQuery
from query import PublicFunction as pf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

"""
该方法用于获取标准信息并入库
"""


class FoundationData:
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
        self.formatted_date = datetime.now().strftime('%Y.%m.%d')
        self.status_dt = {
            '现行': '01',
            '废止': '04'
        }
        self.read_filename = rf'tools/标准号1_urls.xlsx'
        self.data_df = pd.read_excel(self.read_filename)

    def calculate_msg(self, foundation_soup):
        data_dt = {}
        for tag in foundation_soup:
            li_all = tag.find_all('li')

            for li in li_all:
                # 提取键值
                key_p = li.find('p')
                key = key_p.get_text().replace('：', '').strip().replace('\u3000', '')
                # 提取值
                value_h2 = li.find('h2')
                if not value_h2:
                    value_h2 = li.find('span')
                value = value_h2.get_text().strip().replace('\u3000', '') if value_h2 else ""
                # 存储数据
                data_dt[key] = value
        return data_dt

    def make_get(self):
        data_lt = []
        for index, row in self.data_df.iterrows():
            try_num = 3
            url = row.get('链接')
            while try_num > 0:
                try:
                    time.sleep(random.uniform(1, 2))
                    response = requests.get(url=url, headers=self.headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    foundation_soup = soup.find_all("ul", attrs={'class': 'detailedinfo-content-collapse'})
                    data_dt = self.calculate_msg(foundation_soup)
                    print(data_dt)
                    data_lt.append(data_dt)
                    break
                except Exception as e:
                    print(e)
                    time.sleep(random.uniform(1, 2))
        return data_lt

    def select_from_oa(self):
        sql = rf"SELECT * FROM [自收录数据].dbo.[标准库menus]"
        results = pf.query_sql_BidDocument(sql)
        return results

    def select_data(self):
        results = self.select_from_oa()
        menus_dt = {}
        for row in results:
            leibie = row[1]
            leibie_key = row[0]
            menus_dt[leibie] = leibie_key
        return menus_dt

    def insert_data(self, data_df):
        # 数据库连接信息
        connInfo = 'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=FB6.0;UID=saa;PWD=1+2-3..*Qwe!@#'

        # 建立数据库连接
        with pyodbc.connect(connInfo) as conn:
            with conn.cursor() as cursor:
                insesql = """
                        INSERT INTO [自收录数据].[dbo].[标准库_国家行业标准] (
                            [唯一标志], [标题], [全文], [类别], [类别key], [发布部门], [发布日期], 
                            [实施日期], [标准状态], [标准状态key], [来源], [标准分类], [标准分类key], 
                            [中国标准分类号], [国际标准分类号], [标准号], [附件位置], [标准类型], 
                            [价格], [是否免费]
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """

                # 准备参数列表
                params_list = []
                for index, row in data_df.iterrows():
                    row = row.fillna('')
                    time.sleep(random.uniform(0.5, 0.75))
                    jiage = PriceQuery.get_Sell(row['标准号'])
                    print(f"价格: {jiage}")
                    is_free = "002" if jiage != "0" else "001"

                    params_list.append((
                        row['唯一标志'], row['标准名称'], row['全文'], str(row['类别']), str(row['类别key']),
                        row['发布部门'], row['发布日期'].replace('-', '.'), row['实施日期'].replace('-', '.'),
                        str(row['标准状态']), str(row['标准状态key']),
                        row['来源'], row['标准分类'], row['标准分类key'], str(row['中标分类号']),
                        str(row['标准ICS号']),
                        str(row['标准号']), row['附件位置'], row.get('标准类别'), jiage, is_free
                    ))
                    print(row['标准名称'])
                    print("======" * 30)

                # 批量执行插入
                try:
                    cursor.executemany(insesql, params_list)
                    conn.commit()
                    print("所有数据写入成功！！！")
                except pyodbc.Error as ex:
                    print(f"批量写入失败: {ex}")
                    for params in params_list:
                        try:
                            cursor.execute(insesql, params)
                            conn.commit()
                            print(f"【{params[1]}】 单条写入成功！！！")
                        except pyodbc.Error as ex:
                            print(f"单条写入失败: {ex}")
                            print(f"数据: {params}")
                            print("=====" * 20)

    def calculate_data(self, data_lt):
        # 标准码表
        menus_dt = self.select_data()
        for it in data_lt:
            # 唯一标志(标准号+今天日期)
            it['唯一标志'] = it.get('标准号') + self.formatted_date
            # 类别和类别key
            leibie = it.get('标准号')[:2]
            for k, v in menus_dt.items():
                if k[:2] == leibie:
                    it['类别'] = k
                    it['类别key'] = v
                    break
                it['类别'] = None
                it['类别key'] = None

            # 标准状态key
            status_key = it.get('标准状态')
            it['标准状态key'] = self.status_dt.get(status_key)
            if "GB" in it['标准号']:
                it['标准分类'] = '国家标准'
                it['标准分类key'] = '0001'
                it['附件位置'] = f"/国家标准/{it.get('标准号').replace('/', '-')}.pdf"
            else:
                it['标准分类'] = '行业标准'
                it['标准分类key'] = '0002'
                it['附件位置'] = f"/行业标准/{it.get('标准号').replace('/', '-')}.pdf"
            it['来源'] = '新版标准库'
            it['全文'] = f"""<a href="javascript:void(0)" class="" onclick="pdfck()">{it.get('标准号')} {it.get('标准名称')}</a>"""
        data_df = pd.DataFrame(data_lt)
        with pd.ExcelWriter(rf"tools/标准号1_处理结果.xlsx") as writer:
            data_df.to_excel(writer, startrow=0, startcol=0)
        return data_df

    def calculate(self):
        data_lt = self.make_get()
        data_df = self.calculate_data(data_lt)
        # data_df = pd.read_excel(r"E:\JXdata\每月手动数据检查\标准基础信息获取\处理结果\信息_中国标网_2024.10.31 159个-最终.xlsx")
        self.insert_data(data_df)
        print(1)


if __name__ == '__main__':
    obj = FoundationData()
    obj.calculate()
