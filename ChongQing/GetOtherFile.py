import difflib
import re
from bs4 import BeautifulSoup
from datetime import datetime
from botpy import logging
from sqlalchemy import create_engine, text
from query import PublicFunction
import pandas as pd

_log = logging.get_logger()
"""
本方法用于获取重庆市教委会其他文件

https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/
"""


class GetOtherFile:
    def __init__(self, **kwargs):
        self.shouludate = "JX" + str(datetime.now().strftime("%Y.%m.%d"))
        self.pf = PublicFunction
        # 读取页数
        self.num_pages = kwargs.get("read_pages_num")
        # 写入表名
        self.table_name = kwargs.get("write_table_name")
        # 存放路径
        self.save_path_real = kwargs.get("save_path_real")
        # 初始url
        self.start_url = kwargs.get("start_url")
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        # 保留列表
        self.into_lt = ["text-align:right", "text-align:center", "text-align: right", "text-align: center"]
        # 效力级别
        self.level_of_effectiveness = {
            "地方规范性文件": "XP08",
            "地方工作文件": "XP10"
        }
        self.level_of_effectiveness_real = self.level_of_effectiveness.get(kwargs.get("level_of_effectiveness"))
        # 收录来源个人
        self.myself_mark = kwargs.get("lasy_department")
        if not self.level_of_effectiveness_real:
            self.level_of_effectiveness_real = self.level_of_effectiveness['地方规范性文件']
        # 发布部门
        self.department_of_publication = {
            "重庆市司法局": "8;831;83103;831030007",
            "重庆市发展和改革委员会": "8;831;83103;831030003",
            "重庆市教育委员会": "8;831;83103;831030004",
            "重庆市公安局": "8;831;83103;831030151",
            "重庆市民政局": "8;831;83103;831030006",
            "重庆市财政局": "8;831;83103;831030008",
            "重庆市人力资源和社会保障局": "8;831;83103;831030011",
            "重庆市规划和自然资源局": "8;831;83103;831030469",
            "重庆市生态环境局": "8;831;83103;831030034",
            "重庆市科学技术局": "8;831;83103;831030005"
        }
        # 在函数返回为空的时候指定发布部门
        self.lasy_department = self.department_of_publication.get(kwargs.get('lasy_department'))
        # 指定起始页数
        self.read_pages_start = kwargs.get('read_pages_start')
        if not self.read_pages_start:
            self.read_pages_start = 0

    def remove_outer_brackets(self, text_remove, end_phrase):
        """
        删除字符串开头和结尾的括号，并保留 发文字号,并删除发文日期
        :param text_remove:
        :param end_phrase:
        :return: 发文字号
        """
        # 移除开头的括号
        if text_remove.startswith('('):
            text_remove = text_remove[1:]
        # 移除结尾的括号
        if text_remove.endswith(')'):
            text_remove = text_remove[:-1]
        # 找到 "发文字号：" 的结束位置
        start_phrase_end = text_remove.find("：", text_remove.find("发文字号"))
        start_index = start_phrase_end + 1
        # 找到 "成文日期" 的开始位置
        end_phrase_start = text_remove.find(end_phrase)
        if end_phrase_start == -1:
            return text_remove  # 如果没有找到结束短语，则返回原字符串
        # 返回 "发文字号：" 和 "成文日期" 之间的文本
        result = text_remove[start_index:end_phrase_start]
        return result

    def from_title_get(self, str_text):
        # 正则表达式模式
        pattern = r"发文字号：(.*?)成文日期：(.*?)(?=\)|$)"
        # 匹配
        match = re.search(pattern, str_text)
        if match:
            # 提取发文字号
            document_number = match.group(1).strip()
            # 提取成文日期
            document_date = match.group(2).strip()
            document_date = document_date.replace("年", ".").replace("月", ".").replace("日", "")
            return document_number, document_date
        else:
            return None, None

    def title_data_get(self, url):
        """
        用于获取到总页面内容，获取到该页的 标题，发文字号，成文日期
        :return:result_lt：列表套字典，字典装有信息
        """
        class_lt = ['row', 'item clearfix', 'zcwjk-list-c clearfix', 'zcwjk-list-c clearfix cur', 'information-l-content', 'clearfix']
        result_lt = []
        # 获取到总网页内容
        soup_title = self.pf.fetch_url(url=url, headers=self.headers)
        soup_title_all = soup_title.find(["table", "div", 'ul'], class_=["leadership-right rt mt20 overview", "p-rt rt"])
        if soup_title_all:
            soup_title_all = soup_title_all.find_all(['tr', 'div', "li"], class_=class_lt)
            for tag in soup_title_all:
                # 标题
                title_get = tag.find('a', href=True)
                title = title_get.get('title')
                # url 未拼接
                title_url = title_get.get('href')
                data_dt = {
                    "法规标题": title,
                    "法规url": title_url
                }
                result_lt.append(data_dt)
        else:
            soup_title_all = soup_title.find('div', class_="li-4")
            soup_title_all = soup_title_all.find_all('a', href=True)
            for tag in soup_title_all:
                # 标题
                p_tag = tag.find('p')
                title = p_tag.get_text()
                # url 未拼接
                title_url = tag.get('href')
                data_dt = {
                    "法规标题": title,
                    "法规url": title_url
                }
                result_lt.append(data_dt)
        return result_lt

    def zhengwen_get(self, soup):
        # 正文
        class_lt = ['trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_external',
                    'view TRS_UEDITOR trs_paper_default trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_key4format trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_web trs_key4format',
                    'zwxl-article',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_web'
                    ]
        zhengwen = soup.find('div', class_=['zcwjk-xlcon', 'gfxwj-content', 'zcwjk-con', 'zwxl-main', 'zwxl-article','lef border'])
        zhengwen_stat = None
        for it in class_lt:
            zhengwen_stat = soup.find('div', class_=it)
            if zhengwen_stat is not None:
                break
        # 对style标签值进行处理
        if zhengwen_stat:
            soup_ture = self.pf.soup_cal(zhengwen_stat)
            soup_ture = self.pf.remove_nbsp(soup_ture)
            # 去除最后部分的扫一扫和分享标签
            soup_ture = self.remove_specific_tags(soup_ture)
        elif zhengwen:
            soup_ture = self.pf.soup_cal(zhengwen)
            soup_ture = self.pf.remove_nbsp(soup_ture)
            # 去除最后部分的扫一扫和分享标签
            soup_ture = self.remove_specific_tags(soup_ture)
        else:
            _log.error("未找到文章的正文部分！！！！")
            soup_ture = None
        # 处理文中靠右属性
        soup_ture = self.pf.set_right_alignment(soup_ture)
        soup_ture = str(soup_ture)
        return soup_ture

    def remove_specific_tags(self, soup):
        # 找到并删除包含特定文本的 <div>
        div_to_remove = soup.find('div', text='扫一扫在手机打开当前页')
        if div_to_remove:
            div_to_remove.decompose()
        # 删除所有其他的指定标签
        for element in soup.find_all('canvas'):
            element.decompose()
        for a in soup.find_all('a', href="#"):
            a.decompose()
        return soup

    def bumen_get(self, soup):
        bumen_soup = soup.find('table', class_='zwxl-table')
        if not bumen_soup:
            return ';;'
        bumen_soup_all = bumen_soup.find_all('tr')
        for tag in bumen_soup_all:
            biaot = tag.find('td', class_='t1')
            if "发布机构" in biaot.get_text():
                bumen = tag.find('td', class_='t2').get_text()
                if bumen == '市发展改革委':
                    bumen = '重庆市发展和改革委员会'
                bumenall = self.pf.get_sql_menus('831', 'lfbj_fdep_id')
                # 使用difflib找到最接近的匹配项
                closest_match = difflib.get_close_matches(bumen, bumenall.keys(), n=1, cutoff=0.6)
                if closest_match:
                    values = bumenall.get(closest_match[0])
                    fabubumen = self.format_values(values)
                    return fabubumen
        return ';;'

    def format_values(self, values):
        if len(values) == 5:
            return f"{values[0]};{values[:3]};{values}"
        elif len(values) == 9:
            return f"{values[0]};{values[:3]};{values[:5]};{values}"
        else:
            raise ValueError("The input must be either 5 or 9 digits long.")

    def process_strings(self, bumen, bumen1):
        if bumen == ';;' and bumen1 == ';;':
            return ';;'
        elif bumen != ';;' and bumen1 == ';;':
            return bumen
        elif bumen == ';;' and bumen1 != ';;':
            return bumen1
        else:
            return bumen1

    def panduan_title(self, title, table_name):
        # 数据库连接信息
        server = 'localhost'
        database = 'test'
        table_name = table_name
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

    def calculate_category(self, it):
        # 计算类别编号
        full_text = it.get('全文')
        title = it.get('法规标题')
        full_text_soup = BeautifulSoup(full_text, 'html.parser')
        full_text_only = full_text_soup.get_text()
        catagroy = self.pf.catagroy_select(description=full_text_only, titl=title)
        bumen = self.pf.department(Description=full_text_only, title=title, area_num='831')  # 831:重庆地区
        return catagroy, bumen

    def annex_get_all(self, soup, title_any, quanwen, issued_date):
        """
        附件下载函数
        :param issued_date: 发布日期
        :param quanwen: 全文
        :param title_any: 匹配内容的标题
        :param soup: 文章页面soup
        :return:
        """
        download_dt = {}
        download = soup.find('div', class_="zwxl-article")
        if not download:
            return quanwen
        # 查找所有带有href属性的标签
        links = download.find_all(href=True)
        for link in links:
            if '#' in link.get('href'):
                continue
            if title_any in link.get_text():
                continue
            download_dt[link.get_text()] = link.get('href')
        if download_dt:
            for key, value in download_dt.items():
                if not issued_date:
                    continue
                issued_date_real = issued_date.replace('.', '')
                issued_date_real = issued_date_real[:-2]
                url_real = self.start_url + issued_date_real + value.lstrip('.')
                self.pf.annex_get(url=url_real, save_path=key, headers=self.headers, save_path_real=self.save_path_real)
                _log.info(f"写入附件，标题为：{key} ,url为:{url_real}!!!")
        else:
            _log.info(f"没有附件内容需要写入！！！")

        quanwen = str(quanwen)
        zhengwen_div_all = download.find_all('div')
        for tag in zhengwen_div_all:
            if "下载" in tag.get_text():
                a_all = tag.find_all(href=True)
                for a in a_all:
                    if a.get('href') in download_dt.values():
                        a['href'] = ''.join(f"/datafolder/新收录/{datetime.now().strftime('%Y%m')}/{a.get_text()}")
                        quanwen += str(a)
                        quanwen += "<br>"
        return quanwen

    def normalize_sequence(self, sequence_str):
        if "8;8;8;8;" in sequence_str:
            sequence_str = sequence_str.lstrip("8;8;8;")
            sequence_str = sequence_str.lstrip("31;")
        return sequence_str

    def extract_date(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # 查找包含日期的 p 标签
        date_p_tag = soup.find('p', string=lambda text_s: '年' in text_s and '月' in text_s and '日' in text_s)

        if date_p_tag:
            # 提取日期
            date_text = date_p_tag.get_text(strip=True)
            return date_text
        else:
            return None

    def date_and_wordsize(self, it, soup):
        """
        处理发布日期和发文字号
        :param it:
        :param soup:
        :return:
        """
        # 发布日期
        if not it.get('发布日期'):
            it['发布日期'] = self.pf.match_date(it['全文'], soup)
        # 发文字号
        data_dt = self.pf.soup_get_date(soup)

        tag_text = data_dt.get("发文字号")
        if tag_text:
            it["发文字号"] = tag_text
        else:
            it["发文字号"] = None
        return it

    def identification_and_source(self, it, new_get_url, soup):
        """
        处理唯一标识,来源,类别以及发布部门
        :param soup:
        :param it:
        :param new_get_url:
        :return:
        """
        if it.get('发布日期'):
            # 唯一标志
            md5_str = it.get('法规标题') + it.get('发布日期')
            it["唯一标志"] = self.pf.get_md5(md5_str)
        else:
            it["唯一标志"] = None
        # 来源
        it["来源"] = new_get_url
        # 发布部门
        catagroy, bumen = self.calculate_category(it)
        bumen1 = self.bumen_get(soup)
        bumen_real = self.process_strings(bumen, bumen1)
        bumen_real = self.normalize_sequence(bumen_real)
        if bumen_real == ';;':
            it["发布部门"] = self.lasy_department
        else:
            it["发布部门"] = bumen_real
        # 类别
        it["类别"] = catagroy
        return it

    def filter_all(self, new_result_lt):
        for it in new_result_lt:
            new_get_url = self.start_url.rstrip('index.html') + it.get('法规url').lstrip('./')
            del it['法规url']
            if self.panduan_title(it.get('法规标题'), self.table_name):
                _log.info(f"{it.get('法规标题')} 文件已经存在！！！")
                continue
            _log.info(f"需要写入的文章:{it.get('法规标题')}")
            try:
                # soup
                soup = self.pf.fetch_url(new_get_url, headers=self.headers)
                # 正文
                it['全文'] = self.zhengwen_get(soup)
                # 处理发布日期和发文字号
                it = self.date_and_wordsize(it, soup)
                # 处理唯一标志和来源
                it = self.identification_and_source(it, new_get_url, soup)
                # 效力级别
                it["效力级别"] = self.level_of_effectiveness_real
                # 时效性
                it["时效性"] = "01"
                it["实施日期"] = it.get('发布日期')
                # 附件处理
                it['全文'] = self.annex_get_all(soup, it['法规标题'], it['全文'], it.get('发布日期'))
                it['收录来源个人'] = self.myself_mark
            except Exception as e:
                _log.info(f"filter_all发生错误:{e}")
                continue
        # 过滤列表中的字典
        filtered_list = [item for item in new_result_lt if len(item) > 4]
        return filtered_list

    def calculate(self):
        # 有几页就遍历几次
        for i in range(self.read_pages_start, self.num_pages):
            if i == 0:
                new_url = self.start_url
            else:
                new_url = self.start_url + f"index_{i}.html"
            # 获取该页内容信息
            result_lt = self.title_data_get(url=new_url)
            _log.info(f"第{i + 1}页    获取到{len(result_lt)} 篇内容！！！")
            # 过滤已有的文章
            new_result_lt = self.pf.filter(result_lt)
            if not new_result_lt:
                _log.info(f"第{i + 1}页    无内容需要写入！！！")
                continue
            _log.info(f"第{i + 1}页    需要写入的文章有 {len(new_result_lt)} 篇！！！")
            # 统筹整理,写入数据
            filtered_list = self.filter_all(new_result_lt)
            if filtered_list:
                df = pd.DataFrame(filtered_list)
                self.pf.to_mysql(df, self.table_name)
                _log.info(f"第{i + 1}页    {len(filtered_list)}篇文件写入完毕！！！")
            else:
                _log.info(f"第{i + 1}页:   内容已经存在！")


def main():
    data_dt = {
        "start_url": 'https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/',  # 访问路径
        "write_table_name": '重庆市其他文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 20,  # 读取页码总数
        "save_path_real": '重庆市其他文件',  # 附件存放路径,
        "lasy_department": '重庆市教育委员会',  # 在函数返回为空的时候指定发布部门
        "level_of_effectiveness": '地方工作文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
    }
    obj = GetOtherFile(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main()
