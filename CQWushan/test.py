import time
import random
import requests
from bs4 import BeautifulSoup, NavigableString
import hashlib
import pandas as pd
from sqlalchemy import create_engine
import re
import pyodbc


"""
本方法用于获取重庆市巫山县 地方规范性文件
"""
class test:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        self.department_of_publication = {"巫山县人民政府": "8;831;83102"}
        # 类别
        self.category = {""}
        # 效力级别
        self.level_of_effectiveness = {"地方规范性文件": "XP08"}
        # 排除列表
        self.not_lt =["text-align:right","text-align:center"]

    def fetch_url(self, url):
        try:
            # 发送 HTTP GET 请求
            response = requests.get(url, headers=self.headers)
            # 检查请求是否成功
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
        # 返回页面内容
        return response.content

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup

    # def download_image(self, soup):
    #     # 发送HTTP请求获取图片数据
    #     response = requests.get(url)
    #
    #     # 检查响应状态码是否为200（成功）
    #     if response.status_code == 200:
    #         # 以二进制写模式打开文件（如果不存在则创建），并写入图片数据
    #         with open(filename, 'wb') as file:
    #             file.write(response.content)
    #         print(f"图片已成功下载到 {filename}")
    #     else:
    #         print("无法下载图片，请检查URL或网络连接。")


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

    def main_text_retrieval(self, soup):
        """
        获取正文内容信息
        """
        url = "http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcwj/gfxwjhz_2310/w/"
        text_version_all_lt = []
        new_url_lt = []
        department_of_publication_lt = []
        level_of_effectiveness_lt = []
        # 获取文字版下载链接（获取正文）
        text_version_all = soup.find_all('a', target="_blank")
        for link in text_version_all:
            if link.get('href').endswith('.pdf'):
                continue  # 如果是.pdf文件，则跳过本次循环
            text_version = link.get('href').lstrip('./')
            # 判断text_version是否以 "http" 开头
            if text_version.startswith("http"):
                time.sleep(random.randint(0, 1))
                continue
            try:
                new_url = url + text_version
                new_url_lt.append(new_url)
                print(new_url)
                time.sleep(random.randint(1, 2))
                print("休眠1-2秒")
                # 发送 HTTP GET 请求
                response = requests.get(new_url, headers=self.headers)
                # 检查请求是否成功
                response.raise_for_status()
                # 返回页面内容
                soup1 = self.parse_html(response.content)
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
                # 对style标签值进行处理
                soup_ture = self.soup_cal(soup_ture)
                soup_ture = self.remove_nbsp(soup_ture)
                # 将结果集转换为字符串
                result_str = str(soup_ture)
                department_of_publication_lt.append(self.department_of_publication["巫山县人民政府"])
                level_of_effectiveness_lt.append(self.level_of_effectiveness["地方规范性文件"])
                text_version_all_lt.append(result_str)
            except requests.RequestException as e:
                print(f"请求失败: {e}")
                continue
        return text_version_all_lt, new_url_lt, department_of_publication_lt, level_of_effectiveness_lt

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
        # 返回清理后的BeautifulSoup对象
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
        return soup_title_lt, soup_time_lt, soup_text_lt, md5_value_lt

    def remove_unicode_chars(self, s):
        pattern = r'[\u0000-\u001F\u007F-\u009F\u2000-\u206F\u2028-\u2029\uFEFF\uFFF0-\uFFFF]'
        return re.sub(pattern, '', s)

    def filter(self, soup):
        # 获取正文内容
        text_version_all_lt, new_url_lt, department_of_publication_lt, level_of_effectiveness_lt = self.main_text_retrieval(
            soup)
        print("获取正文内容完毕!")
        # 获取基础信息
        soup_title_lt, soup_time_lt, soup_text_lt, md5_value_lt = self.basic_information_acquisition(soup)
        data_dt = {
            "唯一标志": md5_value_lt,
            "法规标题": soup_title_lt,
            "全文": text_version_all_lt,
            "发布日期": soup_time_lt,
            "实施日期": soup_time_lt,
            "发文字号": soup_text_lt,
            "来源": new_url_lt,
            "发布部门": department_of_publication_lt,
            "效力级别": level_of_effectiveness_lt
        }
        # 将字典转换为DataFrame
        df = pd.DataFrame.from_dict(data_dt)
        return df

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
        table_name = 'test_wushan1'
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    def main(self):
        for i in range(6):
            if i == 0:
                url = "http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcwj/gfxwjhz_2310/w/"
            else:
                url = f"http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcwj/gfxwjhz_2310/w/index_{i}.html"
            html_content = self.fetch_url(url)
            print("网页获取完毕！")
            if html_content:
                soup_text = self.parse_html(html_content)
                xinxi_df = self.filter(soup_text)
                self.to_mysql(xinxi_df)
                print(f"第{i + 1}页写入成功")


def test_main():
    obj = test()
    obj.main()


if __name__ == "__main__":
    test_main()
