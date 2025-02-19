import time
from datetime import datetime
import pandas as pd
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
from urllib3 import disable_warnings
from ProcessingMethod import FullFormattingProcess
from ProcessingMethod.预处理 import iscuncunzaif
from ProcessingMethod.编号处理 import *
import pyodbc
import xml.etree.ElementTree as ET
import random
from elasticsearch import Elasticsearch
from ProcessingMethod.PublicFunction import load_config
import GetUserToken
import GetUserCookieNew
import GetUserCookieCplan
import logging
from ProcessingMethod.LoggerSet import logger

"""
该方法用于获取并处理新法速递文章内容并入库
该方法依赖于“附件"文件夹下的xls或者手动获取数据 excel表格
"""
app_config = load_config(os.getenv('FLASK_ENV', 'test'))
ES_HOSTS = app_config.get('es_hosts')
ES_HTTP_AUTH = tuple(app_config.get('es_http_auth').split(':'))

# 创建Elasticsearch客户端
es = Elasticsearch([ES_HOSTS], http_auth=ES_HTTP_AUTH)


class GetDataFa:
    def __init__(self):
        # 设置需要使用的关键字
        kms = ['chl', '新版中央法规', 'chl']
        self.mkm = kms[1]
        self.mkm0 = kms[2]
        script_directory = os.path.dirname(os.path.abspath(__file__))
        config_directory = os.path.join(script_directory, 'ConfigFile')
        self.cookie_file_path = os.path.join(config_directory, 'cookie.txt')
        # 读取xml文件里的cookies
        cookies_path = os.path.join(config_directory, 'cookies.xml')
        self.tree = ET.parse(cookies_path)
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
        self.proxies_url = "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=b9200c80d01ddc746e97430b3d4a46a9&orderNo=GL202403191725045jqovn7t&count=1&isTxt=0&proxyType=1&returnAccount=1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1717379125; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1717558686; JSESSIONID=12C7E253ECC5428DA27CC601E5DD0C62'
        }
        self.access_plan = None

    def get_x_token(self):
        """
        该方法适用于token失效过后自动获取token,依赖于cookie.txt中的值
        :return:
        """
        logger.info("正在获取最新token,这个过程大概需要1分钟!!!")
        # 获取最新token到本地
        function_dict = {
            "A": GetUserToken.calculate,
            "B": GetUserCookieNew.calculate,
            "C": GetUserCookieCplan.calculate
        }
        # 调用选定函数
        function_dict[self.access_plan]()
        # GetUserCookieCplan.calculate()
        with open(self.cookie_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        self.psessionid = content
        self.header1 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': self.psessionid
        }
        logger.info("成功更换为最新token!!!")

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
            logger.info('数据连接失败', e)

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
                if 'vpn_inject_scripts' in anchor_text:
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
        logger.info(f'正在下载附件 {url}')

        # 确保保存路径的父目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # 设置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
            'cookie': vpncode
        }

        # 禁用urllib3的警告
        disable_warnings()

        try:
            with requests.get(url, headers=headers, stream=True, verify=False) as req:
                if req.status_code == 200:
                    total_size = int(req.headers.get('content-length', 0))  # 获取文件总大小
                    block_size = 1024 * 1024  # 每次读取的块大小为1MB
                    t = tqdm(total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(save_path))  # 初始化进度条

                    with open(save_path, "wb") as f:
                        for data in req.iter_content(block_size):
                            t.update(len(data))  # 更新进度条
                            f.write(data)
                    t.close()

                    if total_size != 0 and t.n != total_size:
                        logger.error("ERROR, something went wrong")
                    logger.info(f"该附件下载完毕: [{save_path}]")

                elif req.status_code == 521:
                    logger.error("状态码521 - 需要进一步处理")
                    # 处理状态码521的逻辑可以在此添加

                elif req.status_code == 404:
                    logger.error("下载失败，网页打不开！！！")
                    logger.error(url)

                else:
                    logger.error(f"未知的状态码: {req.status_code}")

        except Exception as e:
            logger.error(f"请求失败: {e}")

    def token_lose_efficacy(self, cookie_count_num):
        logger.info('cookie已失效!!!')
        with open(self.cookie_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        self.psessionid = content
        self.header1 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': self.psessionid
        }
        if cookie_count_num >= 2:
            logger.info('cookie已失效，正在重新获取!!!')
            time.sleep(random.uniform(2, 3))
            self.get_x_token()

    def feach_url(self, link):
        max_attempts = 5
        url_dt = {
            "A": self.vpnurl + link,
            "B": "https://elksslpkulaw.aa.sjuku.top" + link,
            "C": "https://elksslc41982105a8a896422599210c038c4c8elksslauthserver.a6.sjuku.top" + link

        }
        logger.info(f"当前使用的是{self.access_plan}号访问方案")
        url_real = url_dt.get(self.access_plan)
        cookie_count_num = 0

        for attempt in range(max_attempts):
            try:
                time.sleep(random.uniform(2, 3))
                resp = requests.get(url_real, headers=self.header1, verify=False, timeout=20)
                soup = BeautifulSoup(resp.text, 'html.parser')

                # 如果cookie失效，则会被重定向到百度搜索，这里用来判断是否失效
                if '百度搜索' in str(soup):
                    cookie_count_num += 1
                    self.token_lose_efficacy(cookie_count_num)
                    continue

                else:
                    ul = soup.find('div', class_='fields')
                    if not ul:
                        logger.error("未能找到正确内容!重试!")
                        cookie_count_num += 1
                        self.token_lose_efficacy(cookie_count_num)
                        continue
                    ul = ul.find('ul')
                    if "剩余50%未阅读" in ul:
                        logger.error('获取文章不完整!剩余50%未阅读')
                        continue
                    if ul is not None:
                        logger.info('已正确获取到该文章内容!')
                        return soup, ul, url_real
            except Exception as e:
                logger.error('请求失败:', e)
                time.sleep(random.uniform(2, 4))
                continue

    def change_wrap_handle(self, change_wrap):
        """
        处理本法变迁
        :param change_wrap:
        :return:
        """
        result_soup = BeautifulSoup('', 'html.parser')
        li_all = change_wrap.find_all('li')
        for tag in li_all:
            time_tag = tag.find('span', attrs={"class": "time"})
            time_str = time_tag.get_text()
            a_all = tag.find_all(['a', 'span'], onmouseover=True)
            for a_tag in a_all:
                onmouseover_value = a_tag['onmouseover']
                # 找到 "AJI(" 和 ")" 的位置
                start_index = onmouseover_value.find("AJI(") + len("AJI(")
                end_index = onmouseover_value.find(")", start_index)
                # 提取中间的数字
                value = onmouseover_value[start_index:end_index]
                a_tag['href'] = f'javascript:SLC({value},0)'
                a_tag['class'] = 'alink'
                # 删除onmouseover属性
                del a_tag['logcode']
                del a_tag['onmouseover']
                new_str = time_str + " " + a_tag.get_text()
                a_tag.string = new_str
        # 找到所有class为"alink"的标签
        alink_tags = change_wrap.find_all(class_='alink')
        # 将所有class为"alink"的标签添加到新的BeautifulSoup对象中
        for tag in alink_tags:
            if tag.name == 'a':
                result_soup.append(tag)
            else:
                tag.name = 'a'
                result_soup.append(tag)
        return result_soup

    def attachment_processing(self, soup, title, urla, data_dt, types_regulations):
        """
        附件和全文处理函数
        :return:
        """
        formatted_date = datetime.now().strftime("%Y%m")
        if types_regulations:
            file_path = fr"E:/新法速递附件/chl附件/{formatted_date}/"
        else:
            file_path = fr"E:/新法速递附件/lar附件/{formatted_date}/"
        # 检测路径是否存在
        if not os.path.exists(file_path):
            # 如果路径不存在，则创建路径
            os.makedirs(file_path)
            logger.info(f"创建路径: 目录 [{file_path}] 已创建。")
        change_wrap = soup.find('div', attrs={"class": "change-wrap"})
        if change_wrap:
            result_soup = self.change_wrap_handle(change_wrap)
        else:
            result_soup = None
        # TODO 本法变迁输出
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
                    self.public_down(hrefc, file_path + wjm, self.psessionid)
                    time.sleep(random.uniform(2, 4))
                    fujian.append({"Title": title, "SavePath": ysrca, "Url": urla})
                except Exception as e:
                    logger.error(f"附件下载出错： {e}")
                    test.attrs = {'href': ysrca}
                    fujian.append({"Title": title, "SavePath": ysrca, "Url": urla})
        if 'img' in str(full):
            for img in full.find_all('img'):
                ysrc = img.get('src')
                if ysrc:
                    file_name = ysrc.split('/')[-1]
                    file_name = file_name.rstrip('?vpn-1')

                    ysrca = os.path.join('/datafolder/附件/' + self.mkm + '/' + file_name)
                    replaced_full = str(replaced_full).replace(ysrc, ysrca)

                    try:
                        self.public_down(ysrc, file_path + file_name, self.psessionid)
                        fujian.append({"Title": title, "SavePath": ysrca, "Url": ysrc})
                        time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        logger.error(f"Error downloading {ysrc}: {e}")

                    img.attrs = {'src': ysrca}

        #  正文处理
        if len(fujian) != 0:
            full = replaced_full
        full = str(full).replace("附法律依据", '')
        full = str(full).replace("附：相关法律条文            ", '')
        if result_soup:
            full = str(result_soup) + str(full)
        else:
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
            logger.info(f"该文章已经存在于{table_name}表!!!")
            logger.info("=" * 20)
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
            logger.info(f"文章 {data_dt.get('法规标题')} 写入成功！！！")
            logger.info("====" * 20)
        except Exception as e:
            logger.info(f"文章 {data_dt.get('法规标题')} 写入错误:", e)
            logger.info("====" * 20)

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

    def check_elasticsearch_existence(self, title, index):
        """
        检查 Elasticsearch 中是否存在给定标题的文章。

        参数:
        title (str): 文章标题。

        返回:
        bool: 如果文章不存在返回 True，否则返回 False。
        """
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "标题": {
                                    "query": title,
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
        response = es.search(index=index, body=query_body)
        if int(response['hits']['total']) == 0:
            # logger.info(f'文章不存在: {title}')
            return True
        else:
            # logger.info(f'存在文章: {title}')
            return False

    def calculate(self, choose=False, types_regulations=True, access_plan="C"):
        """
        总流程
        :param types_regulations: True为chl收录，False为lar收录
        :param choose: True为自动收录，False为手动收录
        :return: 在 47数据库，FB6.0库 fb_新版中央法规_chl表 中查询插入数据结果
                    47数据库，FB6.0库 fb_新版地方法规_lar 中查询插入数据结果
        """

        if not self.cursor:
            raise Exception('数据库连接失败！')
        self.access_plan = access_plan
        logger.info("开始读取dataframe.")
        # 读取Excel文件
        if choose:
            if types_regulations:
                df = pd.read_excel('附件/chl.xlsx')
                logger.info("本次收录为: chl 自动收录!!!")
            else:
                df = pd.read_excel('附件/lar.xlsx')
                logger.info("本次收录为: lar 自动收录!!!")
        else:
            df = pd.read_excel('附件/手动获取的文章.xlsx')
            logger.info("本次收录为: 手动收录!!!")

        count = 0
        index_t = 'chl' if types_regulations else 'lar'
        # 打印所有标题和链接
        for index, row in df.iterrows():
            titles = row['标题']
            link = row['链接']
            if self.check_elasticsearch_existence(title=titles, index=index_t):
                count += 1
                logger.info(f'[{count}] 标题   {titles}  url为{link}')
                self.process_soup(link, titles, types_regulations)
            else:
                logger.info(f"ES数据库已经存在文章: {titles} ,不予写入!!!")
        logger.info("全部获取完毕！！！")


def main_test(choose_t, types_regulations_t, access_plan):
    """
    :param access_plan: 访问方案
    :param types_regulations_t: True为chl收录，False为lar收录
    :param choose_t: True为自动收录，False为手动收录
    """
    obj = GetDataFa()
    obj.calculate(choose=choose_t, types_regulations=types_regulations_t, access_plan=access_plan)


if __name__ == '__main__':
    choose = True
    types_regulations = True
    access_plan = "C"
    main_test(choose, types_regulations, access_plan)
