import difflib
import random
import re
import time

from bs4 import BeautifulSoup
from datetime import datetime
from botpy import logging
from sqlalchemy import create_engine, text

from query import PublicFunction
import pandas as pd

_log = logging.get_logger()
"""
本方法用于获取重庆市发改委其他文件

url:https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/index.html
"""


class DevelopmentAndReformCommissionOther:
    def __init__(self):
        self.shouludate = "JX" + str(datetime.now().strftime("%Y.%m.%d"))
        self.pf = PublicFunction
        # 初始url
        # self.start_url = 'https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/xzgfxwj/sfzggwxzgfxwj/'
        self.start_url = 'https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/'
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        # 保留列表
        self.into_lt = ["text-align:right", "text-align:center", "text-align: right"]
        # 发布部门
        self.department_of_publication = {
            "重庆市司法局": "8;831;83103;831030007",
            "重庆市发展和改革委员会": "8;831;83103;831030003",
        }
        # # 类别
        # self.category = {"机关工作综合规定": "003;00301"}
        # 效力级别
        self.level_of_effectiveness = {"地方规范性文件": "XP08", "地方工作文件": "XP10"}

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

    def title_data_get(self, url):
        """
        用于获取到总页面内容，获取到该页的 标题，发文字号，成文日期
        :return:result_lt：列表套字典，字典装有信息
        """
        result_lt = []
        # 获取到总网页内容
        soup_title_all = self.pf.fetch_url(url=url, headers=self.headers)
        soup_title_all = soup_title_all.find('div', class_='gkm-crbox')
        soup_title_all = soup_title_all.find_all('ul', class_='xhy-c1item underlines overflows xhy-item1 gl-ul')
        for tag in soup_title_all:
            soup_small = tag.find_all('li', class_='clearfix')
            for tag_1 in soup_small:
                # 标题
                title_get = tag_1.find('a', target="_blank")
                title = title_get.get('title')
                # url 未拼接
                title_url = title_get.get('href')
                # 发布日期
                issued_date_get = tag_1.find('span', class_="rt")
                issued_date = issued_date_get.get_text().replace('-', '.')
                data_dt = {
                    "法规标题": title,
                    "法规url": title_url,
                    "发布日期": issued_date
                }
                result_lt.append(data_dt)
        return result_lt

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
                self.pf.annex_get(url=url_real, save_path=key, headers=self.headers)
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

    def zhengwen_get(self, soup, title):
        # 正文
        class_lt = ['trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_external',
                    ]
        # 正文
        zhengwen = soup.find('div', class_='zwxl-content')
        zhengwen = zhengwen.find('div', class_='zwxl-article')
        if zhengwen:
            for it in class_lt:
                zhengwen_stat = zhengwen.find('div', class_=it)
                if zhengwen_stat is not None:
                    # 对style标签值进行处理
                    soup_ture = self.pf.soup_cal(zhengwen_stat)
                    soup_ture = self.pf.remove_nbsp(soup_ture)
                    soup_ture = str(soup_ture)
                    return soup_ture
            divs = zhengwen.find_all('div')
            soup_ture_div = ""
            if divs:
                soup = BeautifulSoup(features="html.parser")
                divs = zhengwen.find_all('div')
                new_div = soup.new_tag('div')
                for div in divs:
                    new_div.append(div)
                soup.append(new_div)
                soup_ture = soup
                tag_2 = self.pf.soup_cal(soup_ture)
                tag_2 = self.pf.remove_nbsp(tag_2, False)
                soup_out = str(tag_2)
                soup_ture_div = soup_out.replace('扫一扫在手机打开当前页', '')
            ps = zhengwen.find_all('p')
            soup_ture_p = ""
            if ps:
                soup = BeautifulSoup(features="html.parser")
                new_p = soup.new_tag('p')
                for p in ps:
                    new_p.append(p)
                soup.append(new_p)
                soup_ture = soup
                tag_2 = self.pf.soup_cal(soup_ture)
                tag_2 = self.pf.remove_nbsp(tag_2, False)
                soup_out = str(tag_2)
                soup_ture_p = soup_out.lstrip('[').rstrip(']')

            in_lt = ['核准', "备案", "批复", "予以同意", "请示", "审批", "年", "日", "实施", "规定", "招标", "管理",
                     "建设", "公司"]
            for it in in_lt:
                if it in soup_ture_p:
                    return soup_ture_p
            if len(soup_ture_p) > len(soup_ture_div):
                return soup_ture_p
            else:
                return soup_ture_div

    def format_values(self, values):
        if len(values) == 5:
            return f"{values[0]};{values[:3]};{values}"
        elif len(values) == 9:
            return f"{values[0]};{values[:3]};{values[:5]};{values}"
        else:
            raise ValueError("The input must be either 5 or 9 digits long.")

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

    def calculate_category(self, it):
        # 计算类别编号
        full_text = it.get('全文')
        if not full_text:
            return None, None
        title = it.get('法规标题')
        # 确保full_text是一个字符串或字节类型
        if full_text is None:
            full_text = ""
        elif not isinstance(full_text, (str, bytes)):
            full_text = str(full_text)

        if full_text:
            # 重新解析成一个新的 soup 对象
            full_text_soup = BeautifulSoup(full_text, 'html.parser')
            # 使用 get_text() 方法获取所有的文本内容
            full_text_only = full_text_soup.get_text()
            if full_text_only:
                catagroy = self.pf.catagroy_select(description=full_text_only, titl=title)
                bumen = self.pf.department(Description=full_text_only, title=title, area_num='831')  # 831:重庆地区
                return catagroy, bumen
        return None, None

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

    def process_strings(self, bumen, bumen1):
        if bumen == ';;' and bumen1 == ';;':
            return ';;'
        elif bumen != ';;' and bumen1 == ';;':
            return bumen
        elif bumen == ';;' and bumen1 != ';;':
            return bumen1
        else:
            return bumen1

    def fawenzihao_get(self, all_text):
        #
        pattern = r'[一-龥]+〔\d{4}〕\d+号'
        match = re.findall(pattern, all_text)
        if match:
            # _log.info("发文字号找到匹配:", str(match[0]))
            return str(match[0])
        else:
            _log.info("没有发文字号匹配")
            return None

    def filter_all(self, new_result_lt):
        for it in new_result_lt:
            if self.panduan_title(it.get('法规标题'), '发改委其他文件'):
                _log.info(f"{it.get('法规标题')} 文件已经存在！！！")
                _log.info("------------------------------------")
                continue
            sleep = random.uniform(0, 2)
            _log.info(f"休眠{sleep}秒")
            time.sleep(sleep)
            _log.info(f"需要写入的文章:{it.get('法规标题')}")
            new_get_url = self.start_url.rstrip('index.html') + it.get('法规url').lstrip('./')
            del it['法规url']
            soup = self.pf.fetch_url(new_get_url, headers=self.headers)
            try:
                # 正文
                it['全文'] = self.zhengwen_get(soup, it.get('法规标题'))
                # 发文字号
                it['发文字号'] = self.fawenzihao_get(it['全文'])
                # 唯一标志
                md5_str = it.get('法规标题') + it.get('发布日期')
                it["唯一标志"] = self.pf.get_md5(md5_str)
                # 来源
                it["来源"] = new_get_url
                # 发布部门
                catagroy, bumen = self.calculate_category(it)
                bumen1 = self.bumen_get(soup)
                it["发布部门"] = self.process_strings(bumen, bumen1)
                # it["发布部门"] = self.department_of_publication['重庆市发展和改革委员会']
                # 类别
                it["类别"] = catagroy
                # 效力级别
                it["效力级别"] = self.level_of_effectiveness['地方工作文件']
                # 时效性
                it["时效性"] = "01"
                it["实施日期"] = it.get('发布日期')
                # sql = rf"INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[时效性],[来源],[收录时间]) VALUES ('{it['唯一标志']}','{it.get('法规标题')}','{it['全文']}','{it['发布部门']}','{it['类别']}','{it.get('发布日期')}','{it['效力级别']}','{it['实施日期']}','{it['时效性']}','{it['来源']}','{self.shouludate}')"
                # self.pf.save_sql_BidDocument(sql)
                # _log.info(f"文章:{it.get('法规标题')}写入完毕！！！")
                it['全文'] = self.annex_get_all(soup, it['法规标题'], it['全文'], it.get('发布日期'))
            except Exception as e:
                _log.info(f"filter_all发生错误:{e}")
                continue
        # 过滤列表中的字典
        filtered_list = [item for item in new_result_lt if len(item) > 3]
        return filtered_list

    def calculate(self):
        # 有几页就遍历几次
        for i in range(47, 184):
            if i == 0:
                new_url = self.start_url
            else:
                new_url = self.start_url + f"index_{i}.html"
            sleep = random.uniform(0, 5)
            _log.info(f"休眠{sleep}秒")
            time.sleep(sleep)
            # 获取该页内容信息
            try:
                result_lt = self.title_data_get(url=new_url)
                _log.info(f"第{i + 1}页    获取到{len(result_lt)} 篇内容！！！")

                # 过滤已有的文章
                new_result_lt = self.pf.filter(result_lt)
                if not new_result_lt:
                    _log.info(f"第{i + 1}页    无内容需要写入！！！")
                    continue
                _log.info(f"第{i + 1}页    需要写入的文章有 {len(new_result_lt)} 篇！！！")

                # 统筹整理,写入数据
                new_result_lt = self.filter_all(new_result_lt)
                if new_result_lt:
                    df = pd.DataFrame(new_result_lt)
                    self.pf.to_mysql(df, '发改委其他文件')
                    _log.info(
                        f"第{i + 1}页    {len(new_result_lt)}篇文件写入完毕！！！\n ===================================")
                else:
                    _log.info(f"第{i + 1}页    内容已经存在！\n ===================================")
            except Exception as e:
                _log.error(f"第{i + 1}页    发生错误: {e}，\n 跳过该页继续执行!!!!!==================")
                continue


def main():
    obj = DevelopmentAndReformCommissionOther()
    obj.calculate()


if __name__ == '__main__':
    main()
