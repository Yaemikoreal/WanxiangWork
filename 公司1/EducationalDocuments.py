# -*- coding: utf-8 -*-
import difflib
import re
from bs4 import BeautifulSoup
from datetime import datetime
from botpy import logging
from sqlalchemy import create_engine, text
from 公司1 import PublicFunction
import pandas as pd
# from .writein import calculate
_log = logging.get_logger()
"""
本方法用于获取重庆市教育委员会行政规范性文件
本文件是模版获取文件

url:https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/gfxwj/
"""


class EducationalDocuments:
    def __init__(self, **kwargs):
        self.shouludate =  str(datetime.now().strftime("%Y.%m.%d"))+'LYJ'
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
            "重庆市科学技术局": "8;831;83103;831030005",

            "重庆市市住房城乡建委":"8;831;83103;831030467",
            "重庆市市城市管理局": "8;831;83103;831030466",
            "重庆市市市交通运输委": "8;831;83103;831030015",
            "重庆市市水利局": "8;831;83103;831030016",
            "重庆市市农业农村委": "8;831;83103;831030035",
            "重庆市市商务委": "8;831;83103;831030402",
            "重庆市市文化旅游委": "8;831;83103;831030040",
            "重庆市市卫生健康委": "8;831;83103;831030039",
            "市退役军人事务局": "8;831;",
            "重庆市市应急管理局": "8;831;83103;831030037",
            "重庆市市审计局": "8;831;83103;831030242",
            "重庆市市政府外办": "8;831;83103;831030232",
        }
        # 在函数返回为空的时候指定发布部门
        self.lasy_department = self.department_of_publication.get(kwargs.get('lasy_department'))
        # # 类别
        # self.category = {"机关工作综合规定": "003;00301"}
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
            return document_number,document_date
        else:
            return None,None

    def title_data_get(self, url):
        """
        用于获取到总页面内容，获取到该页的 标题，发文字号，成文日期
        :return:result_lt：列表套字典，字典装有信息
        """
        issued_num,issued_date = None,None
        result_lt = []
        # 获取到总网页内容
        soup_title = self.pf.fetch_url(url=url, headers=self.headers)
        soup_title_all = soup_title.find(["table", "div"], class_='zcwjk-list')
        soup_title_all = soup_title_all.find_all(['tr', 'div'], class_=['row', 'item clearfix', 'zcwjk-list-c clearfix',
                                                                        'zcwjk-list-c clearfix cur'])
        for tag in soup_title_all:
            title_get = tag.find(['p', 'div'], class_=['tit', 'title', 'nr'])
            # 标题
            title = title_get.get_text()
            title = title.replace('\n', '').replace(' ', '')

            # url 未拼接
            title_url_get = tag.find('a', target="_blank")
            title_url = title_url_get.get('href')

            for label in ['p', 'div']:
                issued_num_get = tag.find(label, class_='info')

                if issued_num_get and label == 'p':
                    # 发文字号
                    issued_num = issued_num_get.get_text()
                    issued_num = self.remove_outer_brackets(issued_num, "成文日期 ")

                    # 发布日期
                    issued_date = issued_num_get.find('span', class_='time').get_text()
                    issued_date = issued_date.lstrip("成文日期 ：")
                    issued_date = issued_date.replace("年", ".").replace("月", ".").replace("日", "")
                    break

                elif issued_num_get and label == 'div':
                    # 发文字号
                    issued_num = issued_num_get.find('span', class_='zh').get_text()
                    issued_num = issued_num.lstrip("（发文字号：")

                    # 发布日期
                    issued_date = issued_num_get.find('span', class_='time').get_text()
                    issued_date = issued_date.lstrip('成文日期 ：').rstrip('）')
                    issued_date = issued_date.replace("年", ".").replace("月", ".").replace("日", "")
                    break
                elif issued_num_get:
                    title = tag.find('p', class_='nr')
                    if not title:
                        continue
                    title = title.get_text()
                    issued_num_get = tag.find('p', class_=['info', 'xx'])
                    # 发文字号
                    issued_num_text = issued_num_get.get_text()
                    issued_num = self.remove_outer_brackets(issued_num_text, "成文日期 ")
                    # 正则表达式匹配
                    pattern = r'(\d{4}年\d{1,2}月\d{1,2}日)'
                    match = re.search(pattern, issued_num_text)
                    issued_date = match.group(1).replace("年", ".").replace("月", ".").replace("日", "")
                    break
            if not issued_num or not issued_date:
                issued_num, issued_date = self.from_title_get(title)
            if ")" in title or "(" in title:
                # 特殊处理重庆市民政局的样式
                if "渝民" in issued_num:
                    title = title_get.find('p', class_="nr").get_text()
            data_dt = {
                "法规标题": title,
                "法规url": title_url,
                "发文字号": issued_num,
                "发布日期": issued_date
            }
            result_lt.append(data_dt)
        return result_lt

    def zhengwen_get(self, soup,title):
        # 正文
        class_lt = ['trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_external'
                    ]
        zhengwen = soup.find('div', class_=['zcwjk-xlcon', 'gfxwj-content', 'zcwjk-con'])
        if not zhengwen:
            _log.error("未找到文章的正文部分！！！！")
        for it in class_lt:
            zhengwen_stat = zhengwen.find('div', class_=it)
            if zhengwen_stat is not None:
                break
        if '重庆市国土房管局重庆市房改办关于城镇住房制度改革工作若干问题的通知' == title:
            # 查找并删除具有特定样式的<span>标签
            for style in ["font-family:方正姚体; font-size:42pt; letter-spacing:-7pt",
                          "font-family:方正姚体; font-size:42pt; letter-spacing:-6.5pt",
                          "font-family:方正姚体; font-size:42pt; letter-spacing:-6pt"]:
                for span in zhengwen.find_all('span', style=style):
                    span.decompose()
            ee = zhengwen.find_all('p',style='margin-top:0pt; margin-bottom:0pt; line-height:20pt')[0]
            ee.decompose()
        # 对style标签值进行处理
        if zhengwen:
            soup_ture = self.pf.soup_cal(zhengwen)
            soup_ture = self.pf.remove_nbsp(soup_ture)
        else:
            soup_ture = None

        soup_ture = str(soup_ture)
        return soup_ture

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
        database = 'store'
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
        # 重新解析成一个新的 soup 对象
        full_text_soup = BeautifulSoup(full_text, 'html.parser')
        # 使用 get_text() 方法获取所有的文本内容
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
                it['全文'] = self.zhengwen_get(soup,it.get('法规标题'))
                # 唯一标志
                md5_str = it.get('法规标题') + it.get('发布日期')
                it["唯一标志"] = self.pf.get_md5(md5_str)
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
                if not it['类别']:
                    it['类别']='096;09601'
                # 效力级别
                it["效力级别"] = self.level_of_effectiveness['地方规范性文件']
                # 时效性
                it["时效性"] = "01"
                it["实施日期"] = it.get('发布日期')
                it['全文'] = self.annex_get_all(soup, it['法规标题'], it['全文'], it.get('发布日期'))
                it['全文'] = self.pf.downfile_img(self.headers,it["来源"], it['全文'],it['全文'])
            except Exception as e:
                _log.info(f"filter_all发生错误:{e}")
                continue
        # 过滤列表中的字典
        filtered_list = [item for item in new_result_lt if len(item) > 3]
        states=True
        return filtered_list,states

    def calculate(self):
        # 有几页就遍历几次
        for i in range(self.read_pages_start,self.num_pages):
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
            filtered_list,states= self.filter_all(new_result_lt)
            if filtered_list and states:
                for filt in filtered_list:
                    sql = rf"INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES ('{filt['唯一标志']}','{filt['法规标题']}','{filt['全文']}','{filt['发布部门']}','{filt['类别']}','{filt['发布日期']}','{filt['效力级别']}','{filt['实施日期']}','{filt['发文字号']}','{filt['时效性']}','{filt['来源']}','{self.shouludate}')"
                    self.pf.save_sql_BidDocument(sql)
            elif states==False:
                df = pd.DataFrame(filtered_list)
                self.pf.to_mysql(df, self.table_name)
                _log.info(f"第{i + 1}页    {len(filtered_list)}篇文件写入完毕！！！")
            else:
                _log.info(f"第{i + 1}页:   内容已经存在！")


def main():
    data_dt = {
        "start_url": 'https://zfcxjw.cq.gov.cn/zwgk_166/zfxxgkmls/zcwj/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 8,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市住房城乡建委'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()
    data_dt = {
        "start_url": 'https://cgj.cq.gov.cn/zwgk_173/zfxxgkml/zcfg/xzgfxwj_396426/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 7,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市城市管理局'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()
    data_dt = {
        "start_url": 'https://jtj.cq.gov.cn/zwgk_240/zfxxgkml/zcwj/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 7,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市市交通运输委'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://slj.cq.gov.cn/zwgk_250/zfxxgkml/zcfg/gfxwj1/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 5,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市水利局'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://sww.cq.gov.cn/zwgk_247/zfxxgkmlrk/zcwj/xzffxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 5,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市商务委'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://whlyw.cq.gov.cn/zwgk_221/zfgkzcwj/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 4,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市文化旅游委'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://wsjkw.cq.gov.cn/zwgk_242/zfxxgkml/zcwj/xzgfxwj2/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 17,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市卫生健康委'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://tyjrswj.cq.gov.cn/zwgk_529/zfxxgkml/zcwj/gfxwj/tyjsswjzcwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 1,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '市退役军人事务局'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://yjj.cq.gov.cn/zwgk_230/zfxxgkml/zcwj/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 1,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市应急管理局'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://sjj.cq.gov.cn/zwgk/zcwj/ghxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 1,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市审计局'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()

    data_dt = {
        "start_url": 'https://zfwb.cq.gov.cn/zwgk_162/fdzdgknr/zcwj2/xzxgfwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 1,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市市政府外办'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main()
