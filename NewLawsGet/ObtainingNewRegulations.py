import time
from datetime import datetime
import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
from urllib3 import disable_warnings
from NewLawsGet.ProcessingMethod import FullFormattingProcess
from NewLawsGet.ProcessingMethod.预处理 import iscuncunzaif
from NewLawsGet.ProcessingMethod.编号处理 import *
import pyodbc
import xml.etree.ElementTree as ET
import random
from elasticsearch import Elasticsearch
from query.PublicFunction import load_config
import GetUserToken
import logging
"""
该方法用于获取并处理新法速递文章内容并入库
该方法依赖于“附件"文件夹下的xls或者手动获取数据 excel表格
"""
app_config = load_config(os.getenv('FLASK_ENV', 'test'))
ES_HOSTS = app_config.get('es_hosts')
ES_HTTP_AUTH = tuple(app_config.get('es_http_auth').split(':'))

# 创建Elasticsearch客户端
es = Elasticsearch([ES_HOSTS], http_auth=ES_HTTP_AUTH)
# 配置日志输出到控制台
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class GetDataFa:
    def __init__(self):
        # 设置需要使用的关键字
        kms = ['chl', '新版中央法规', 'chl']
        self.mkm = kms[1]
        self.mkm0 = kms[2]
        # 设置代理
        self.proxies = {
            'http': 'http://127.0.0.1:1080',
            'https': 'http://127.0.0.1:1080',
        }
        # 读取xml文件里的cookies
        self.tree = ET.parse('./cookies.xml')
        self.root = self.tree.getroot()
        self.psessionid = self.root.find('cookies').text.replace('\n', '').replace(' ', '')
        # 读取VPN URL
        self.vpnurl = self.root.find('html').text.strip()
        # 设置请求头
        self.header1 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': self.psessionid
        }
        connInfo = 'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=FB6.0;UID=saa;PWD=1+2-3..*Qwe!@#'
        conn = pyodbc.connect(connInfo)
        self.cursor = conn.cursor()
        # 时效性字典
        self.timeliness_dt = {
            '现行有效': '01',
            '尚未施行': '04',
            '失效': '02',
            '部分修订': '03'
        }

    def get_x_token(self):
        """
        该方法适用于token失效过后自动获取token,依赖于cookie.txt中的值
        :return:
        """
        logging.info("正在获取最新token,这个过程大概需要1分钟!!!")
        # 获取最新token到本地
        GetUserToken.calculate()
        with open('cookie.txt', 'r', encoding='utf-8') as file:
            content = file.read()
        self.psessionid = content
        self.header1 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': self.psessionid
        }
        logging.info("成功更换为最新token!!!")

    def elasticsearch_is_exist(self, tittle):
        # 构建查询请求体
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "标题": {
                                    "query": tittle,
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

        # 执行搜索请求
        resp = es.search(index='chl', body=body)

        # 检查搜索结果是否存在
        if int(resp['hits']['total']) == 0:
            return True
        else:
            # 取消注释以打印所有匹配的标题
            # for i in resp['hits']['hits']:
            return False

    def iscuncunzaifss(self, issql):
        try:
            return iscuncunzaif(issql)
        except Exception as e:
            logging.info('数据连接失败', e)

            return self.iscuncunzaifss(issql)

    def changeinfo(self, html):
        # 检查html是否为None
        if html is not None:
            # 查找并移除包含"附件预览"的<div>标签
            for div_tag in html.find_all('div'):
                if '附件预览' in str(div_tag):
                    div_tag.extract()

            # 处理所有的<a>标签
            for anchor in html.find_all('a'):
                anchor_text = str(anchor)

                # 移除包含特定字符串的<a>标签
                if 'vpn_inject_scripts' in anchor_text or 'tiao_' in anchor_text:
                    anchor.extract()
                    continue

                href = anchor.get('href')
                onmouseover = anchor.get('onmouseover')

                if onmouseover is None:
                    continue

                # 提取onmouseover属性中的信息
                pattern = re.compile(r'AJI\((.*?)\)')
                match = re.search(pattern, onmouseover)
                if not match:
                    continue

                right = match.group(1)
                right_values = right.split(',')

                if '/chl/' in str(href) or '/lar/' in str(href):
                    rginfo = ''
                    if len(right_values) >= 2:
                        for value in right_values:
                            rginfo += str(int(float(value))) + ','
                        rginfo = rginfo[:-1]
                    else:
                        rginfo = right_values[0] + ',0'

                    anchor.attrs = {
                        'href': f'javascript:SLC({rginfo})',
                        'onmouseover': f'javascript:AJI({rginfo})',
                        'class': 'alink'
                    }
            # 移除特定的字体大小样式
            html = str(html).replace('font-size: 16px;', '')
            html = str(html).replace('font-size: 18px;', '')

        return html

    def public_down(self, url, save_path, vpncode):
        logging.info(f'正在下载附件 {url}')
        # 确保保存路径的父目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
            'cookie': vpncode
        }
        # 禁用urllib3的警告
        disable_warnings()
        # 发送GET请求
        req = requests.get(url, headers=headers, stream=True)

        try:
            if req.status_code == 200:
                total_size = int(req.headers.get('content-length', 0))  # 获取文件总大小
                block_size = 1024  # 每次读取的块大小为1KB
                t = tqdm(total=total_size, unit='iB', unit_scale=True)  # 初始化进度条

                with open(save_path, "wb") as f:
                    for data in req.iter_content(block_size):
                        t.update(len(data))  # 更新进度条
                        f.write(data)
                t.close()

                if total_size != 0 and t.n != total_size:
                    logging.error("ERROR, something went wrong")
                return "ok"
            elif req.status_code == 521:
                logging.error("状态码521 - 需要进一步处理")
                # 处理状态码521的逻辑可以在此添加
            elif req.status_code == 404:
                logging.error("下载失败，网页打不开！！！")
                logging.error(url)
                return "fail, 下载失败，网页打不开！！！"
        except Exception as e:
            logging.error(e)

    def feach_url(self, link):
        max_attempts = 5
        url_a = self.vpnurl + link
        logging.info(f"Fetching URL: {url_a}")

        cookie_count_num = 0

        for attempt in range(max_attempts):
            try:
                time.sleep(random.uniform(2, 4))
                resp = requests.get(url_a, headers=self.header1, verify=False)
                soup = BeautifulSoup(resp.text, 'html.parser')

                # 如果cookie失效，则会被重定向到百度搜索，这里用来判断是否失效
                if '百度搜索' in str(soup):
                    cookie_count_num += 1
                    logging.info('cookie已失效!!!')
                    with open('cookie.txt', 'r', encoding='utf-8') as file:
                        content = file.read()
                    self.psessionid = content
                    self.header1 = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
                        'Cookie': self.psessionid
                    }
                    if cookie_count_num >= 2:
                        logging.info('cookie已失效，正在重新获取!!!')
                        self.get_x_token()
                    continue

                else:
                    ul = soup.find('div', class_='fields').find('ul')
                    if ul is not None:
                        return soup, ul, url_a
            except Exception as e:
                logging.error('请求失败:', e)
                time.sleep(random.uniform(2, 4))
                continue

    def attachment_processing(self, soup, title, urla, data_dt, types_regulations):
        """
        附件和全文处理函数
        :return:
        """
        formatted_date = datetime.now().strftime("%Y%m")
        if types_regulations:
            file_path = f"/新法速递附件/chl附件/{formatted_date}/"
        else:
            file_path = f"/新法速递附件/lar附件/{formatted_date}/"
        full = soup.find('div', id='divFullText')
        full = self.changeinfo(full)
        full = BeautifulSoup(full, "html.parser")
        [s.extract() for s in full.find_all('button')]
        [s.extract() for s in full.find_all('small')]
        fujian = []
        replaced_full = full
        for test in full.find_all('a', href=re.compile(
                '.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz|PDF|ppt)+$')):
            ysrc = test.get('href')
            hrefc = ysrc
            ysrcs = ysrc.split("/")
            wjm = ysrcs[len(ysrcs) - 1]
            if '?' in wjm:
                wjm = wjm.split('?')
                wjm = wjm[0]
            if hrefc:
                ysrca = '/datafolder/附件/' + self.mkm + '/' + wjm
                replaced_full = str(replaced_full).replace(hrefc, ysrca)
                try:
                    self.public_down(hrefc, './附件' + file_path + wjm, self.psessionid)
                    time.sleep(random.uniform(2, 4))
                    fujian.append({"Title": title, "SavePath": ysrca, "Url": urla})
                except Exception as e:
                    logging.error(f"附件下载出错： {e}")
                    test.attrs = {'href': ysrca}
                    fujian.append({"Title": title, "SavePath": ysrca, "Url": urla})
        if 'img' in str(full):
            for img in full.find_all('img'):
                # 跳过带有 style 属性的 img 标签
                if img.has_attr('style'):
                    continue

                ysrc = img.get('src')

                file_name = ysrc.split('/')[-1]
                file_name = file_name.rstrip('?vpn-1')

                ysrca = os.path.join('/datafolder/附件/' + self.mkm + '/' + file_name)
                replaced_full = str(replaced_full).replace(ysrc, ysrca)

                try:
                    self.public_down(ysrc, os.path.join('./', file_path, file_name), self.psessionid)
                    fujian.append({"Title": title, "SavePath": ysrca, "Url": ysrc})
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    logging.error(f"Error downloading {ysrc}: {e}")

                img.attrs = {'src': ysrca}

        #  正文处理
        if len(fujian) != 0:
            full = replaced_full
        full = str(full).replace("附法律依据", '')
        full = str(full).replace("附：相关法律条文            ", '')
        full = str(full)
        b = re.compile(r"'")
        full = b.sub('', str(full))
        full = b.sub('窗体底端', str(full))
        full = b.sub('窗体顶端', str(full))

        tszd2 = re.compile(
            r'<br/>1</div>|<br/>2</div>|<br/>3</div>|<br/>4</div>|<br/>5</div>|法信超链|法宝|</button>|</small>|dbsText|http://129.0.0.24:9000')
        ists2 = tszd2.search(full)
        if ists2:
            full = FullFormattingProcess.full_calculate(full)
            data_dt['全文'] = full
        else:
            fuu = re.compile("法宝联想")
            full = fuu.sub('智能关联', full)
            tihuan = re.compile('\'')
            fujian = tihuan.sub('"', str(fujian))
            full = FullFormattingProcess.full_calculate(full)
            data_dt['附件'] = fujian
            data_dt['全文'] = full
        timemc = str(time.strftime('%Y%m%d', time.localtime(time.time())))
        data_dt['收录日期'] = timemc
        return data_dt

    def publishing_department_handle(self, search_date):
        """
        发布部门处理函数
        :param search_date:
        :return:
        """
        partment = ''
        department = search_date.find_all('a', bdclick="")
        de_list = []
        fin = re.compile(r'IssueDepartment=(?P<redepartment>.*?)&amp;way=textBasic')
        result = fin.finditer(str(department))
        for i in result:
            de_list.append(i.group('redepartment'))
        if len(de_list) >= 2:
            process_list = []
            for department in de_list:
                if len(department) == 1:
                    pass
                elif len(department) == 3:
                    department = department[0] + ";" + department
                elif len(department) == 5:
                    department = department[0] + ";" + department[0:3] + ";" + department
                elif len(department) == 7:
                    department = department[0] + ";" + department[0:3] + ";" + department[
                                                                               0:5] + ";" + department
                elif len(department) == 9:
                    department = department[0] + ";" + department[0:3] + ";" + department[
                                                                               0:5] + ";" + department[
                                                                                            0:7] + ";" + department
                elif len(department) == 11:
                    department = department[0] + ";" + department[0:3] + ";" + department[
                                                                               0:5] + ";" + department[
                                                                                            0:7] + ";" + department[
                                                                                                         0:9] + ";" + department
                process_list.append(department)
            for asd in process_list:
                partment += str(asd) + ';'
            department = partment.rstrip(';')
        else:
            for department in de_list:
                if len(department) == 1:
                    pass
                elif len(department) == 3:
                    department = department[0] + ";" + department
                elif len(department) == 5:
                    department = department[0] + ";" + department[0:3] + ";" + department
                elif len(department) == 7:
                    department = department[0] + ";" + department[0:3] + ";" + department[
                                                                               0:5] + ";" + department
                elif len(department) == 9:
                    department = department[0] + ";" + department[0:3] + ";" + department[
                                                                               0:5] + ";" + department[
                                                                                            0:7] + ";" + department
                elif len(department) == 11:
                    department = department[0] + ";" + department[0:3] + ";" + department[
                                                                               0:5] + ";" + department[
                                                                                            0:7] + ";" + department[
                                                                                                         0:9] + ";" + department
        department = str(department).strip()
        return department

    def category_handle(self, search_date):
        """
        类别处理函数
        :param search_date:
        :return:
        """
        law_class = search_date.find_all('a', bdclick="")
        law_list = []
        fin2 = re.compile(r'Category=(?P<re_law>.*?)&amp;way=textBasic')
        result = fin2.finditer(str(law_class))
        for i in result:
            law_list.append(i.group('re_law'))
        if len(law_class) >= 2:
            process_list2 = []
            for law in law_list:
                if len(law) == 1:
                    pass
                elif len(law) == 3:
                    law_class = law[0] + ';' + law
                elif len(law) == 5:
                    law_class = law[0] + ';' + law[0:3] + ';' + law
                elif len(law) == 7:
                    law_class = law[0] + ';' + law[0:3] + ';' + law[0:5] + ';' + law
                elif len(law) == 9:
                    law_class = law[0] + ';' + law[0:3] + ';' + law[0:5] + ';' + law[
                                                                                 0:7] + ';' + law
                process_list2.append(law_class)
            aaa = ''
            for asd in process_list2:
                aaa += str(asd) + ';'
            law_class = aaa.rstrip(';')
        else:
            for law in law_list:
                if len(law) == 1:
                    pass
                elif len(law) == 3:
                    law_class = law[0] + ';' + law
                elif len(law) == 5:
                    law_class = law[0] + ';' + law[0:3] + ';' + law
                elif len(law) == 7:
                    law_class = law[0] + ';' + law[0:3] + ';' + law[0:5] + ';' + law
                elif len(law) == 9:
                    law_class = law[0] + ';' + law[0:3] + ';' + law[0:5] + ';' + law[
                                                                                 0:7] + ';' + law
        # 候补逻辑
        law_class = re.sub('.*?;', '', str(law_class), count=1)
        law_class_s = law_class.split(';')
        if len(law_class_s) > 2:
            law_class = str(law_class_s[0] + ';' + law_class_s[1])
        return law_class

    def select_sql(self, data_dt, table_name='fb_新版中央法规_chl'):
        select_table_name = table_name
        if data_dt.get('发文字号'):
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
                收录日期 
            FROM 
                {select_table_name}
            WHERE 
                法规标题 = ? AND 
                发文字号 = ? AND 
                发布日期 = ? 
            """
            params = (data_dt.get("法规标题"), data_dt.get('发文字号'), data_dt.get('公布日期'))
        elif data_dt.get('公布日期'):
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
                            收录日期 
                        FROM 
                            {select_table_name} 
                        WHERE 
                            法规标题 = ? AND 
                            发布日期 = ? 
                        """
            params = (data_dt.get("法规标题"), data_dt.get('公布日期'))
        else:
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
                            收录日期 
                        FROM 
                            {select_table_name} 
                        WHERE 
                            法规标题 = ? 
                        """
            params = (data_dt.get("法规标题"))
        # 执行查询
        self.cursor.execute(query_sql, params)
        # 获取查询结果
        results = self.cursor.fetchall()
        # 如果该条数据已经存在于数据库，返回True
        if results:
            logging.info(f"该文章已经存在于{table_name}表!!!")
            logging.info("=" * 20)
            return True
        return False

    def write_to_sql(self, data_dt, table_name):
        try:
            insesql = f"""
                INSERT INTO {table_name} (
                    法规标题,
                    发文字号,
                    类别,
                    发布日期,
                    实施日期,
                    发布部门,
                    时效性,
                    效力级别,
                    法宝引证码,
                    全文,
                    url,
                    唯一标志,
                    附件,
                    收录日期
                )
                VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                );"""
            params_lt = (
                data_dt.get('法规标题'), data_dt.get('发文字号'), data_dt.get('法规类别'), data_dt.get('公布日期'),
                data_dt.get('施行日期'), data_dt.get('制定机关'), data_dt.get('时效性'),
                data_dt.get('效力位阶'), data_dt.get('唯一标志'), data_dt.get('全文'), data_dt.get('url'),
                data_dt.get('唯一标志'), data_dt.get('附件'), data_dt.get('收录日期'))
            self.cursor.execute(insesql, params_lt)
            self.cursor.commit()
            logging.info(f"文章 {data_dt.get('法规标题')} 写入成功！！！")
            logging.info("=" * 20)
        except Exception as e:
            logging.info(f"文章 {data_dt.get('法规标题')} 写入错误:", e)
            logging.info("=" * 20)

    def process_soup(self, link, titles, types_regulations):
        """
        对单篇文章进行统一处理
        :param types_regulations: True为chl收录，False为lar收录
        :param titles: 法规标题
        :param link: 文章url
        :return:
        """
        data_dt = {'法规标题': titles}
        # 检查该条数据是否已经存在于数据库
        if types_regulations:
            table_name = 'fb_新版中央法规_chl'
            if self.select_sql(data_dt, table_name):
                return
        else:
            table_name = 'fb_新版地方法规_lar'
            if self.select_sql(data_dt, table_name):
                return

        time.sleep(random.uniform(2, 4))

        soup, ul, urla = self.feach_url(link)
        if not soup:
            return
        data_dt['url'] = urla
        title = soup.find('h2', class_='title').text.rstrip(' ').lstrip(' ').strip()
        date_li = ul.find_all('li')

        # 对单篇文章进行处理
        for search_date in date_li:
            search_date_text = str(search_date)
            if '公布日期' in search_date_text:
                publica_date = search_date.get('title')
                if publica_date:
                    publica_date = publica_date.strip()
                else:
                    publica_date = search_date.get_text().lstrip('公布日期：')
                data_dt['公布日期'] = publica_date

            if '施行日期' in search_date_text:
                execute_date = search_date.get('title')
                if execute_date:
                    execute_date = execute_date.strip()
                else:
                    execute_date = search_date.get_text().lstrip('施行日期：')
                data_dt['施行日期'] = execute_date

            if '发文字号' in search_date_text:
                contant_number = search_date.get('title')
                if contant_number:
                    contant_number = contant_number.strip()
                else:
                    contant_number = search_date.get_text().lstrip('发文字号：')
                data_dt['发文字号'] = contant_number

            if '时效性' in search_date_text:
                timeliness = search_date.find('span')
                if timeliness:
                    timeliness = timeliness.get('title')
                    timeliness = self.timeliness_dt.get(timeliness)
                else:
                    timeliness = search_date.find('a', class_='timelinessDic')
                    timeliness = timeliness.get_text()
                    timeliness = self.timeliness_dt.get(timeliness)
                data_dt['时效性'] = timeliness

            if '法规类别' in search_date_text:
                law_class = self.category_handle(search_date)
                data_dt['法规类别'] = law_class

            if '效力位阶' in search_date_text:
                effectiveness_level = search_date.find('a', bdclick="").get('href')
                effectiveness_level = effectiveness_level.split('Aggs.EffectivenessDic=')[-1].split('&')[0]
                if len(effectiveness_level) == 4:
                    pass
                elif len(effectiveness_level) == 6:
                    effectiveness_level = effectiveness_level[0:4] + ';' + effectiveness_level
                data_dt['效力位阶'] = effectiveness_level

            if '制定机关' in search_date_text:
                department = self.publishing_department_handle(search_date)
                data_dt['制定机关'] = department
        # 唯一标志
        unique_identifier = soup.find('div', class_="content").find('div', class_="info").find('a').text
        unique_identifier = unique_identifier.split('.')[2]
        data_dt['唯一标志'] = unique_identifier

        issql = True
        if issql:
            # 附件处理
            data_dt = self.attachment_processing(soup, title, urla, data_dt, types_regulations)
            data_dt = self.full_formatting(data_dt)
            if not self.select_sql(data_dt, table_name):
                self.write_to_sql(data_dt, table_name)

    def full_formatting(self, data_dt):
        """
        正文格式二次处理
        :param data_dt:
        :return:
        """
        full = data_dt.get('全文')
        full = FullFormattingProcess.new_full_calculate(full)
        data_dt['全文'] = full
        return data_dt

    def calculate(self, choose=False, types_regulations=True):
        """
        总流程
        :param types_regulations: True为chl收录，False为lar收录
        :param choose: True为自动收录，False为手动收录
        :return: 在 47数据库，FB6.0库 fb_新版中央法规_chl表 中查询插入数据结果
                    47数据库，FB6.0库 fb_新版地方法规_lar 中查询插入数据结果
        """

        if not self.cursor:
            raise Exception('数据库连接失败！')

        # 读取Excel文件
        if choose:
            if types_regulations:
                df = pd.read_excel('附件/chl.xlsx')
                logging.info("本次收录为: chl 自动收录!!!")
            else:
                df = pd.read_excel('附件/lar.xlsx')
                logging.info("本次收录为: lar 自动收录!!!")
        else:
            df = pd.read_excel('附件/手动获取的文章.xlsx')
            logging.info("本次收录为: 手动收录!!!")

        count = 0
        # 打印所有标题和链接
        for index, row in df.iterrows():
            count += 1
            titles = row['标题']
            link = row['链接']
            logging.info(f'[{count}] 标题   {titles}  url为{link}')
            self.process_soup(link, titles, types_regulations)
        logging.info("全部获取完毕！！！")


def main_test(choose_t, types_regulations_t):
    """
    :param types_regulations_t: True为自动收录，False为手动收录
    :param choose_t: True为chl收录，False为lar收录
    """
    obj = GetDataFa()
    obj.calculate(choose=choose_t, types_regulations=types_regulations_t)


if __name__ == '__main__':
    choose = True
    types_regulations = False
    main_test(choose, types_regulations)
