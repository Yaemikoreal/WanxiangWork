import time
import random
import requests
from bs4 import BeautifulSoup, NavigableString, Comment
import hashlib
import pandas as pd
from sqlalchemy import create_engine, text
import re
import pyodbc
from botpy import logging

_log = logging.get_logger()

"""
本方法用于获取重庆市 巫山县 的 人大代表建议办理复函 收录
"""


class WushanStandardizedDocuments:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        self.department_of_publication = {"重庆市其他机构": "8;831;83103"}
        # 类别
        self.category = {"机关工作综合规定": "003;00301"}
        # 效力级别
        self.level_of_effectiveness = {"地方规范性文件": "XP08", "地方工作文件": "XP10"}
        # 保留列表
        self.not_lt = ["text-align:right", "text-align:center", "text-align: right"]
        #
        self.table_name = 'chlour'

    def fetch_url(self, url):
        cl_num = 3
        for it in range(cl_num):
            try:
                sleep = random.uniform(2, 4)
                time.sleep(sleep)
                _log.info(f"休眠{sleep}秒")
                # 发送 HTTP GET 请求
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                if response.status_code == 200:
                    # 返回页面内容
                    soup = BeautifulSoup(response.content, 'html.parser')
                    return soup
            except pyodbc.OperationalError as e:
                _log.info(f"出错！      {e}")
                sleep = random.uniform(2, 4)
                time.sleep(sleep)
                _log.info(f"休眠{sleep}秒")
                _log.info("==========================")
                if it == cl_num - 1:
                    _log.info("该网站内容无法获取")
                    _log.info(f"网站url:  {url}")
        return soup

    def determine(self, style):
        not_in_lt = ['font-family', 'margin-top', 'margin-bottom', 'font-size', 'line-height']
        for it in not_in_lt:
            if it in style:
                return True
        return False

    def soup_cal(self, soup_ture):
        # 移除所有style属性，但保留居中，靠右，加粗
        for tag in soup_ture.find_all(True):
            # text_1 = tag.get_text()
            style = tag.get('style')
            data_index = tag.get('data-index')
            if data_index:
                del tag['data-index']
            if style:
                if self.determine(style):
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
                            continue
                    else:
                        del tag['style']
                        continue
                else:
                    if 'text-align' in style:
                        # 获取当前元素的style属性值
                        style_value = tag['style']
                        # 将style值分割成多个样式
                        styles = style_value.split(';')
                        if "text-align:left" in styles:
                            del tag['style']
                            continue
                    else:
                        del tag['style']
                        continue
        return soup_ture

    def panduan_title(self, title):
        # 数据库连接信息
        server = 'localhost'
        database = 'test'
        table_name = self.table_name
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
            _log.info(f"数据库连接或查询失败: {e}")

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
                new_string = tag.string.replace(" ", "")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace("  ", "")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(" ", "")
                tag.string.replace_with(new_string)
        a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
        soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
        # 遍历所有的<span>标签
        for span in soup.find_all('span'):
            # 如果span标签的文本为空，则移除它
            if not span.get_text().strip():
                span.decompose()
        for p in soup.find_all('p'):
            # 如果标签的文本为空，则移除它
            if not p.get_text().strip():
                p.decompose()
        # 删除所有的<img>标签
        for img in soup.find_all('img'):
            img.decompose()
        for st in soup.find_all('script'):
            st.decompose()
        # 删除抄送
        for it in soup.find_all('p'):
            tag_text = it.get_text()
            if "抄送" in tag_text:
                it.decompose()
        # 将 soup 转换为字符串
        html_str = str(soup)
        # 使用正则表达式移除 HTML 注释
        html_str_without_comments = re.sub(r'<!--(.*?)-->', '', html_str, flags=re.DOTALL)
        # 如果需要，可以重新解析成一个新的 soup 对象
        soup = BeautifulSoup(html_str_without_comments, 'html.parser')
        # # 为最终落款格式未靠右的文章添加靠右
        # soup = self.add_right(soup, ['局', '会'])
        # soup = self.add_right(soup, ['年', '月', '日'])
        return soup

    def add_right(self, soup, in_lt):
        # 给非靠右标签添加靠右属性
        # in_lt = ['局', '会']
        found = False  # 添加一个标志变量来记录是否找到了符合条件的标签
        for tag in reversed(soup.find_all('p')):
            text_1 = tag.get_text()
            for it in in_lt:
                if it in text_1:
                    style_1 = tag.get('style')
                    if style_1 and 'right' not in style_1:
                        # 如果已有 style 属性且不包含 'right'，则修改 style 属性
                        tag['style'] = 'text-align: right;'
                    elif not style_1:
                        # 如果没有 style 属性，则添加
                        tag['style'] = 'text-align: right;'
                    found = True  # 设置标志变量为 True
                    break  # 找到匹配后跳出内部循环
            if found:
                break  # 找到第一个匹配项后跳出外层循环
        return soup

    def get_md5(self, string):
        m = hashlib.md5()
        m.update(string.encode('utf-8'))
        return m.hexdigest()

    def zhengwen_get(self, soup):
        # 正文
        class_lt = ['trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web'
                    ]
        zhengwen = soup.find('div', class_='a24Detail')
        for it in class_lt:
            zhengwen_stat = zhengwen.find('div', class_=it)
            if zhengwen_stat is not None:
                break
        # 对style标签值进行处理
        if zhengwen:
            soup_ture = self.soup_cal(zhengwen)
            soup_ture = self.remove_nbsp(soup_ture)
        else:
            soup_ture = None
        return soup_ture

    def filter(self, new_url, release_date, name):
        data_dt = {
            "唯一标志": [],
            "法规标题": [],
            "全文": [],
            "发布日期": [],
            "实施日期": [],
            "来源": [],
            "发布部门": [],
            "效力级别": [],
            "时效性": [],
            "类别": []
        }
        soup_text = self.fetch_url(new_url)
        # 正文
        zhengwen = self.zhengwen_get(soup_text)
        zhengwen = str(zhengwen)
        data_dt["全文"].append(zhengwen)
        # 发布日期，实施日期
        implementation_date = release_date
        data_dt["发布日期"].append(implementation_date)
        data_dt["实施日期"].append(implementation_date)
        # 唯一标志
        md5_str = name + release_date
        md5_value = self.get_md5(md5_str)
        data_dt["唯一标志"].append(md5_value)
        # 法规标题
        soup_title = name
        data_dt["法规标题"].append(soup_title)
        # 来源
        new_url = new_url
        data_dt["来源"].append(new_url)
        # 发布部门
        bumen_all_lt = self.department_of_publication['重庆市其他机构']
        data_dt["发布部门"].append(bumen_all_lt)
        # 类别
        leibie = self.category['机关工作综合规定']
        data_dt["类别"].append(leibie)
        # 效力级别
        xiaoli = self.level_of_effectiveness['地方工作文件']
        data_dt["效力级别"].append(xiaoli)
        # 时效性
        shixiao = "01"
        data_dt["时效性"].append(shixiao)
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
            _log.info(f"Connection error: {e}")
            exit()
        table_name = self.table_name
        df.to_sql(name=table_name, con=engine, if_exists='append', index=False)

    def starts_with_dot_slash(self, s):
        return s.startswith("./")

    def get_url_dt(self, wushan_url, num):
        sleep = random.uniform(2, 4)
        time.sleep(sleep)
        _log.info(f"休眠{sleep}秒")
        url_dt = {}
        soup_text = self.fetch_url(wushan_url)
        soup = soup_text.find('div', class_='rigCon')
        a_all = soup.find_all('a', target="_blank")
        for it in a_all:
            any_url = it.get('href')
            if "#" in any_url:
                continue
            any_title = it.get('title')
            if self.starts_with_dot_slash(any_url):
                any_url = any_url.lstrip('./')
                if num == 0:
                    # 处理第一页时直接拼接
                    any_url = wushan_url + any_url
                else:
                    wushan_url_1 = wushan_url.rstrip(f"index_{num}.html")
                    any_url = wushan_url_1 + any_url
            else:
                long_url = 'http://www.cqws.gov.cn/'
                any_url = long_url + any_url
            release_date = it.find('span').text
            release_date = release_date.replace('-', '.')
            url_dt[any_title] = []
            url_dt[any_title].append(any_url)
            url_dt[any_title].append(release_date)
        return url_dt

    def liucheng(self, new_url, release_date, name):
        data_dt = self.filter(new_url, release_date, name)
        stat = data_dt['全文'][0]
        if stat != "None":
            # 将字典转换为DataFrame
            df = pd.DataFrame.from_dict(data_dt)
            self.to_mysql(df)
            _log.info(f"{name} 的文件已经处理入库！")
            _log.info("------------------------")
        else:
            _log.info(f"{name}文件正文获取结果为空!!!")
            _log.info(f"{name}文件地址为：{new_url}!!!")

    def main(self, all_imp):
        for it in range(10):
            _log.info(f"当前正在处理第 {it + 1} 页内容!!!")
            if it != 0:
                all_imp_1 = all_imp + f'index_{it}.html'
                url_dt = self.get_url_dt(all_imp_1, it)
            else:
                url_dt = self.get_url_dt(all_imp, it)
            for name, url_date in url_dt.items():
                _log.info(f"正在处理的文件 {name} 的地址为: {url_date[0]} ")
                if self.panduan_title(name):
                    _log.info(f"{name} 文件已经存在！！！")
                    _log.info("------------------------")
                    continue
                _log.info(f"正在尝试 {name} 文件的处理和写入！")
                url = url_date[0]
                release_date = url_date[1]
                self.liucheng(url, release_date, name)
        _log.info("完毕！！！！！！")


def test_main(all_imp):
    obj = WushanStandardizedDocuments()
    obj.main(all_imp)


if __name__ == "__main__":
    all_imp = 'http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/jyta/jytabl/rddbjybl/'
    test_main(all_imp)
