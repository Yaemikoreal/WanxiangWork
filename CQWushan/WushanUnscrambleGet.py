import json
import time
import random
from datetime import datetime
import pyquery
import requests
from bs4 import BeautifulSoup, NavigableString
import hashlib
import pandas as pd
from sqlalchemy import create_engine, text
import pyodbc
from soup_cal import _remove_attrs


"""
本方法用于获取重庆市巫山县人民政府的政策解读文件
"""
class WushanUnscrambleGet:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        self.department_of_publication = {"巫山县人民政府": "8;831;83102"}
        # 解读类别
        self.category = "093;093002"
        # 发布部门
        self.bumen = "8;831;83103"
        # 保留列表
        self.not_lt = ["text-align:right", "text-align:center"]
        # 拼接用url
        self.pin_url = "http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcjd_1/"

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    def get_soup(self, new_url):
        cl_num = 3
        for it in range(cl_num):
            try:
                time.sleep(random.randint(2, 3))
                # 发送 HTTP GET 请求
                response = requests.get(new_url, headers=self.headers)
                response.raise_for_status()
                if response.status_code == 200:
                    # 返回页面内容
                    soup = self.parse_html(response.content)
                    # soup = _remove_attrs(soup)
                    return soup
            except pyodbc.OperationalError as e:
                print(f"出错！      {e}")
                print("休眠4-6秒")
                print("==========================")
                time.sleep(random.randint(4, 6))
                if it == cl_num - 1:
                    print("该网站内容无法获取")
                    print(f"网站url:  {new_url}")

    def get_md5(self, string):
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()

    def wushan_get(self):
        url = "http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcjd_1/myjson.json?myjson=myjson&&myjson=myjson&_=1723777300181"
        # 发送 HTTP GET 请求
        response = requests.get(url, headers=self.headers)
        # 检查请求是否成功
        response.raise_for_status()
        soup_str = response.text
        # 移除开头的 "myjson(" 和结尾的 ")"
        trimmed_str = soup_str.replace("myjson(", "").replace(")", "")
        # 将所有单引号替换为双引号
        trimmed_str = trimmed_str.replace("'", '"')
        # 将剩余的字符串解析为字典
        data = json.loads(trimmed_str)
        data_lt = data.get("datas")
        return data_lt

    def remove_nbsp(self, soup):
        # 遍历所有的文本节点
        for tag in soup.find_all(True):
            if tag.string and isinstance(tag.string, NavigableString):
                # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
                # 将非换行空格替换为空格
                new_string = tag.string.replace(' ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(' ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace('?', " ")
                tag.string.replace_with(new_string)
        # 返回清理后的BeautifulSoup对象
        return soup

    def analyze_article(self, one_url):
        is_http = one_url.startswith("http")
        if is_http:
            return None, None
        new_url = self.pin_url + one_url.lstrip("./")
        # 获取文章网页soup
        soup = self.get_soup(new_url)
        soup = self.remove_nbsp(soup)
        if not soup:
            ones_fbbm, ones_zw = None, None
            return ones_fbbm, ones_zw
        fbbm_soup = soup.find('div', class_='a24Bt')
        # 获取script标签中的文本
        script_text = fbbm_soup.script.string
        # 使用pyquery解析整个HTML字符串
        doc = pyquery.PyQuery(script_text)
        source_info_element = doc('span')
        fbbm_text = source_info_element.text()
        ones_fbbm = fbbm_text.lstrip("来源：")
        # 定义可能的类名组合
        class_names = [
            'view TRS_UEDITOR trs_paper_default trs_word',
            'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
            'view TRS_UEDITOR trs_paper_default trs_word',
            'view TRS_UEDITOR trs_paper_default trs_word trs_web',
            'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web'
        ]
        ones_zw = None
        for class_name in class_names:
            ones_zw = soup.find('div', class_=class_name)
            if ones_zw:
                break
        if not ones_zw:
            print(1)
        return ones_fbbm, ones_zw

    def panduan_title(self, title):
        # 数据库连接信息
        server = 'localhost'
        database = 'test'
        # Integrated Security=True启用Windows身份验证
        connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
        # 创建连接
        try:
            engine = create_engine(connection_string)
            # 查询table_name = 'wushan_unscramble'中的“标题”列中是否有title值
            title_to_check = title
            query = text("SELECT COUNT(*) FROM wushan_unscramble WHERE 标题 = :title")
            with engine.connect() as connection:
                result = connection.execute(query, {"title": title_to_check}).scalar()

            if result > 0:
                return True
            else:
                return False

        except Exception as e:
            print(f"数据库连接或查询失败: {e}")

    def processing_integrating_data(self, data_lt):
        count = 0
        data_all_dt = {
            "唯一标志": [],
            "标题": [],
            "全文": [],
            "发布日期": [],
            "发布部门": [],
            "类别": [],
            "收录日期": []
        }
        # 获取并格式化当前日期
        formatted_date = datetime.now().strftime('%Y.%m.%d')
        if not data_lt:
            return
        for ones in data_lt:
            # 标题
            one_title = ones.get('title')
            if "政策解读" in one_title:
                if any(keyword in one_title for keyword in ["发布会", "一图读懂", "视频"]) or self.panduan_title(
                        one_title):
                    print(f"文件 {one_title} 已经存在或不符合条件！！！")
                    continue
                count += 1
                print(f"编号:{count}, 标题:{one_title}")
                print("------------------------------")
                # 获取正文所用的拼接url
                one_url = ones.get('url')

                # 发布部门和初始正文（未处理）
                ones_fbbm, ones_zw = self.analyze_article(one_url)
                # 发布日期
                one_fbrq = ones.get('fbrq').replace("-", ".")
                # 类别
                one_classname = ones.get('classname')
                # 唯一标志
                one_md5 = self.get_md5(one_title + one_fbrq)
                if ones_zw:
                    data_all_dt['唯一标志'].append(one_md5)
                    data_all_dt['标题'].append(one_title)
                    data_all_dt['全文'].append(ones_zw)
                    data_all_dt['发布日期'].append(one_fbrq)
                    data_all_dt['发布部门'].append(self.bumen)
                    data_all_dt['类别'].append(self.category)
                    data_all_dt['收录日期'].append(formatted_date)
                else:
                    print(f"标题:{one_title}的正文为空！！！")
                    print(f"地址为：{one_url}")
                    print("===============================")
        return data_all_dt

    def integrate_styles(self, data_all_dt):
        text_lt = data_all_dt.get("全文")
        for text1 in text_lt:
            time.sleep(1)
            # 移除所有style属性，但保留居中，靠右，加粗
            if text1:
                for tag in text1.find_all(True):
                    style = tag.get('style')
                    if style:
                        if 'font-family' in style:
                            if 'text-align' in style:
                                # 获取当前元素的style属性值
                                style_value = tag['style']
                                # 将style值分割成多个样式
                                styles = style_value.split(';')
                                new_styles = []
                                for it in styles:
                                    if it.strip() in self.not_lt:
                                        new_styles.append(it.strip())
                                # 重新组合样式
                                if new_styles:
                                    tag['style'] = '; '.join(new_styles)
                                else:
                                    del tag['style']
                            else:
                                del tag['style']
                        else:
                            if 'text-align' in style:
                                # 获取当前元素的style属性值
                                style_value = tag['style']
                                # 将style值分割成多个样式
                                styles = style_value.split(';')
                                if "text-align:left" or "text-align: left" in styles:
                                    del tag['style']
                            else:
                                del tag['style']
                    data_index = tag.get('data-index')
                    if data_index:
                        del tag["data-index"]
        data_all_dt["全文"] = text_lt
        # 使用列表推导式将所有元素转换为字符串
        data_all_dt["全文"] = [str(item) for item in data_all_dt["全文"]]
        return data_all_dt

    def split_list(self, lst, n):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]



    def to_mysql(self, df):
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
        table_name = 'wushan_unscramble'
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    def filter(self):
        # 获取接口响应内容
        print("获取接口响应内容!")
        soup_data_lt = self.wushan_get()
        # 整合处理数据内容
        sublists_method_lt = self.split_list(soup_data_lt, 20)
        for it in sublists_method_lt:
            data_all_dt = self.processing_integrating_data(it)
            print("整合处理数据内容！")
            # 整合处理正文内容以及格式
            data_all_dt = self.integrate_styles(data_all_dt)
            print("整合处理正文内容以及格式！")
            if not data_all_dt.get('标题'):
                print("可写入数据为空！！！")
                print("------------------------------------------")
                continue
            # 转换为DataFrame
            print("转换为DataFrame！")
            df = pd.DataFrame.from_dict(data_all_dt)
            print("df构建完成，写入中~")
            self.to_mysql(df)
            print("------------------------------------------")
            time.sleep(3)

    def main(self):
        self.filter()


def test_main():
    obj = WushanUnscrambleGet()
    obj.main()


if __name__ == "__main__":
    test_main()
