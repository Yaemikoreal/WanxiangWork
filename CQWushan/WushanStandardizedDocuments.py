import time
import random
import requests
from bs4 import BeautifulSoup, NavigableString
import hashlib
import pandas as pd
from sqlalchemy import create_engine, text
import re
import pyodbc


"""
本方法用于获取重庆市巫山县人民政府地方规范性文件
"""

class WushanStandardizedDocuments:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        self.department_of_publication = {"巫山县人民政府": "8;831;83102"}
        # 类别
        self.category = {""}
        # 效力级别
        self.level_of_effectiveness = {"地方规范性文件": "XP08"}
        # 保留列表
        self.not_lt = ["text-align:right", "text-align:center"]

    def fetch_url(self, url):
        try:
            # 发送 HTTP GET 请求
            response = requests.get(url, headers=self.headers)
            # 检查请求是否成功
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
        # 返回页面内容
        return soup

    def soup_cal(self, soup_ture):
        # 移除所有style属性，但保留居中，靠右，加粗
        for tag in soup_ture.find_all(True):
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
                        if "text-align:left" in styles:
                            del tag['style']
                    else:
                        del tag['style']
        return soup_ture

    def get_soup(self, new_url):
        cl_num = 3
        for it in range(cl_num):
            try:
                time.sleep(random.randint(2, 3))
                print("休眠2-3秒")
                # 发送 HTTP GET 请求
                response = requests.get(new_url, headers=self.headers)
                response.raise_for_status()
                if response.status_code == 200:
                    # 返回页面内容
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return soup
            except pyodbc.OperationalError as e:
                print(f"出错！      {e}")
                print("休眠4-6秒")
                print("==========================")
                time.sleep(random.randint(4, 6))
                if it == cl_num - 1:
                    print("该网站内容无法获取")
                    print(f"网站url:  {new_url}")

    def panduan_title(self, title):
        # 数据库连接信息
        server = 'localhost'
        database = 'test'
        table_name = 'wushan_standardized'
        # Integrated Security=True启用Windows身份验证
        connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
        # 创建连接
        try:
            engine = create_engine(connection_string)
            query = text(f"SELECT COUNT(*) FROM {table_name} WHERE 法规标题 = :title")
            with engine.connect() as connection:
                result = connection.execute(query, {"title": title}).scalar()
            if result > 0:
                return True
            else:
                return False

        except Exception as e:
            print(f"数据库连接或查询失败: {e}")

    def extract_date(self, str1):
        # 定义日期的正则表达式模式
        pattern = r'(\d{4})年(\d{1,2})月(\d{1,2})日'
        # 在字符串中搜索匹配项
        match = re.search(pattern, str1)
        if match:
            # 从匹配结果中提取年月日
            year, month, day = match.groups()
            # 使用 zfill 方法确保月份和日期始终为两位数字
            formatted_date = f"{year}.{month.zfill(2)}.{day.zfill(2)}"
            return formatted_date
        else:
            return None

    def find_tag_with_text(self, soup, pattern=r"起施行"):
        # 创建正则表达式编译器
        regex = re.compile(pattern)
        # 查找所有匹配的标签
        for tag in soup.find_all(string=regex):
            # 获取匹配的标签
            matching_tag = tag.parent
            matching_tag = matching_tag.parent
            # 提取所有的文本并合并成一个字符串
            text1 = matching_tag.get_text(separator='')
            # 打印匹配的标签
            shixing_date = self.extract_date(text1)
            return shixing_date
        return 0

    def main_text_retrieval(self, soup, new_url):
        """
        获取正文内容信息
        """
        url = new_url
        text_version_all_lt = []
        new_url_lt = []
        department_of_publication_lt = []
        level_of_effectiveness_lt = []
        shixing_date_lt = []
        shixiao_lt = []
        # 获取文字版下载链接（获取正文）
        text_version_all = soup.find_all('a', target="_blank")
        for link in text_version_all:
            if link.get('title'):
                continue
            if link.get('href').endswith('.pdf'):
                continue  # 如果是.pdf文件，则跳过本次循环
            text_version = link.get('href').lstrip('./')
            # 判断text_version是否以 "http" 开头
            if text_version.startswith("http"):
                time.sleep(random.randint(0, 1))
                continue
            title = link.find("p", class_="tit")
            title = title.text
            if self.panduan_title(title):
                print(f"{title} 文件已经存在！！！")
                continue
            try:
                new_url = url + text_version
                new_url_lt.append(new_url)
                print(new_url)
                soup1 = self.get_soup(new_url)
                soup2 = soup1.find(class_="zcwjk-xlcon")
                soup3 = soup2.find(class_="trs_editor_view TRS_UEDITOR trs_paper_default trs_external")
                if not soup3:
                    soup_ture = soup2
                    # 找到所有的<script>标签
                    scripts = soup2.find_all('script')
                    if scripts:
                        for script in scripts:
                            script.decompose()
                else:

                    soup_ture = soup3
                # 匹配施行日期，如果文章中没有提及，则返回0
                shixing_date = self.find_tag_with_text(soup_ture)
                shixing_date_lt.append(shixing_date)
                # 对style标签值进行处理
                soup_ture = self.soup_cal(soup_ture)
                soup_ture = self.remove_nbsp(soup_ture)
                # 将结果集转换为字符串
                result_str = str(soup_ture)
                department_of_publication_lt.append(self.department_of_publication["巫山县人民政府"])
                level_of_effectiveness_lt.append(self.level_of_effectiveness["地方规范性文件"])
                # 时效性 现行有效01
                shixiao_lt.append("01")
                text_version_all_lt.append(result_str)
            except requests.RequestException as e:
                print(f"请求失败: {e}")
                continue
        return text_version_all_lt, new_url_lt, department_of_publication_lt, level_of_effectiveness_lt,shixing_date_lt,shixiao_lt

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
                new_string = tag.string.replace('  ', " ")
                tag.string.replace_with(new_string)
        a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
        soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
        # 遍历所有的<span>标签
        for span in soup.find_all('span'):
            # 如果span标签的文本为空，则移除它
            if not span.get_text().strip():
                span.decompose()
        return soup

    def calculate(self, soup_all, stat, class_):
        soup_title_lt = []
        if class_:
            soup_title = soup_all.find_all(stat, class_=class_)
        else:
            soup_title = soup_all.find_all(stat)
        for i in soup_title:
            text_title = i.get_text()
            soup_title_lt.append(text_title)
        return soup_title_lt

    def get_md5(self, string):
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()

    def unique_identifier(self, soup_title_lt, soup_time_lt):
        md5_value_lt = []
        # 使用 zip 函数组合两个列表
        combined_list = [a + b for a, b in zip(soup_title_lt, soup_time_lt)]
        for i in combined_list:
            md5_value = self.get_md5(i)
            md5_value_lt.append(md5_value)
        return md5_value_lt

    # 定义一个函数来转换日期格式
    def convert_date_format(self, date_str):
        # 使用字符串分割来提取年、月、日
        year, month, day = date_str.split("年")[0], date_str.split("年")[1].split("月")[0], \
            date_str.split("月")[1].split("日")[0]
        # 返回新的日期格式
        return f"{year}.{month}.{day}"

    def basic_information_acquisition(self, soup):
        """
        基础信息获取
        :return:
        """
        soup_all = soup.find(class_="zcwjk-list")
        # 法规标题
        soup_title_lt = self.calculate(soup_all, 'p', 'tit')
        # 发布日期和发文字号
        soup_time_text_lt = self.calculate(soup_all, 'span', None)
        # 使用列表推导式筛选出以'发文字号：'开头的字符串，并去掉'发文字号：'以及'成文日期 ：'
        soup_time_lt = [item[len('成文日期 ：'):] for item in soup_time_text_lt if item.startswith('成文日期 ：')]
        # 应用转换函数到每个日期上
        soup_time_lt = [self.convert_date_format(date) for date in soup_time_lt]
        soup_text_lt = [item[len('发文字号：'):] for item in soup_time_text_lt if item.startswith('发文字号：')]
        # 唯一标志（32位md5值（标题+发布日期））
        md5_value_lt = self.unique_identifier(soup_title_lt, soup_time_lt)
        count = 0
        for it in soup_title_lt:
            if self.panduan_title(it):
                print(f"{it} 文件已经存在！！！")
                del soup_title_lt[count]
                del soup_time_lt[count]
                del soup_text_lt[count]
                del md5_value_lt[count]
            count += 1
        return soup_title_lt, soup_time_lt, soup_text_lt, md5_value_lt

    def remove_unicode_chars(self, s):
        pattern = r'[\u0000-\u001F\u007F-\u009F\u2000-\u206F\u2028-\u2029\uFEFF\uFFF0-\uFFFF]'
        return re.sub(pattern, '', s)

    def filter(self, soup, new_url):
        # 获取正文内容
        text_version_all_lt, new_url_lt, department_of_publication_lt, level_of_effectiveness_lt, shixing_date_lt, shixiao_lt \
            = self.main_text_retrieval(soup, new_url)
        print("获取正文内容完毕!")
        # 获取基础信息
        soup_title_lt, soup_time_lt, soup_text_lt, md5_value_lt = self.basic_information_acquisition(soup)
        for i in range(len(shixing_date_lt)):
            if shixing_date_lt[i] == 0:
                shixing_date_lt[i] = soup_time_lt[i]
        data_dt = {
            "唯一标志": md5_value_lt,
            "法规标题": soup_title_lt,
            "全文": text_version_all_lt,
            "发布日期": soup_time_lt,
            "实施日期": shixing_date_lt,
            "发文字号": soup_text_lt,
            "来源": new_url_lt,
            "发布部门": department_of_publication_lt,
            "效力级别": level_of_effectiveness_lt,
            "时效性": shixiao_lt
        }

        return data_dt

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
        table_name = 'wushan_standardized'
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    def get_url_dt(self):
        url_dt = {}
        wushan_url = 'http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcwj/gfxwjhz_2310/'
        soup_text = self.fetch_url(wushan_url)
        soup = soup_text.find('div', class_='xzgfxwj_231025')
        a_all = soup.find_all('a', target="_blank")
        for it in a_all:
            any_url = it.get('href')
            if "#" in any_url or any_url == "//www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcwj/gfxwjhz_2310/w/":
                continue
            any_title = it.text
            any_url = "http:" + any_url
            url_dt[any_title] = any_url
        return url_dt

    def liucheng(self, new_url):
        soup_text = self.fetch_url(new_url)
        print("网页获取完毕！")
        data_dt = self.filter(soup_text, new_url)
        if data_dt['全文']:
            # 将字典转换为DataFrame
            df = pd.DataFrame.from_dict(data_dt)
            self.to_mysql(df)
            print(df)
        else:
            print("没有需要写入的信息!!!")

    def main(self):
        url_dt = self.get_url_dt()
        for name, url in url_dt.items():
            self.liucheng(url)
            print(f"{name} 的文件已经处理入库！")
            print("------------------------")


def test_main():
    obj = WushanStandardizedDocuments()
    obj.main()


if __name__ == "__main__":
    test_main()
