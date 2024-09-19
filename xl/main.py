# coding:utf-8
from datetime import datetime
import re
import hashlib

import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import etree
from clear_content import  main_test as main_clean_cal
from pyquery.pyquery import PyQuery as pq
from query import PublicFunction
from retrying import retry
from botpy import logging
from elasticsearch import Elasticsearch


_log = logging.get_logger()

es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


class MainCal:
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
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", }
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
            "重庆市住房和城乡建设委员会":"8;831;83103;831030467"

        }
        # 在函数返回为空的时候指定发布部门
        self.lasy_department = self.department_of_publication.get(kwargs.get('lasy_department'))
        # 收录来源个人
        self.myself_mark = kwargs.get("lasy_department")
        # 部门
        self.level_of_effectiveness_real = self.level_of_effectiveness.get(kwargs.get("level_of_effectiveness"))
        # 指定起始页数
        self.read_pages_start = kwargs.get('read_pages_start')
        if not self.read_pages_start:
            self.read_pages_start = 0
        self.pf = PublicFunction
        self.download_dt = {}
        self.shixiaoxing=kwargs.get("shixiaoxing")
        self.area_num=kwargs.get("area_num")

    #得到主页面的所有href
    def main(self,new_result_lt):
        filter_lt = []
        for i in new_result_lt:
            url = 'https://zfcxjw.cq.gov.cn/zwgk_166/zfxxgkmls/zcwj/xzgfxwj'+i['法规url'].replace('./','/')        #https://zfcxjw.cq.gov.cn/zwgk_166/zfxxgkmls/zcwj/xzgfxwj/202301/t20230110_11483778.html
        # response = requests.get(url, headers=self.headers)
        # response.encoding = "utf-8"
        # tree=etree.HTML(response.text)
        # tr_list=tree.xpath('//td[@class="title"]//a')
        # href_list=[]
        # for tr in tr_list:
        #     title=tr.xpath('./p/text()')[0]
        #     href='https://sjj.cq.gov.cn/zwgk/zcwj/ghxwj'+tr.xpath('./@href')[0].replace('./','/')
        #     fazihao=tr.xpath('./p/span[1]/text()')[0]
        #     chengwen_time=tr.xpath('./p[@class="info"]/span[2]/text()')[0]
        #     href_list.append(href)
            title=i['法规标题']
            fazihao=i['发文字号']
            chengwen_time=i['发布日期']
            data_dict = self.parile_content(url, title, fazihao, chengwen_time)
            filter_lt.append(data_dict)
        return filter_lt





    #清洗开头，从<p标签开始之后都拿到，如果没有找到<p>标签，返回原字符串或空字符串
    def space_clear(self,space_clear_html):
            # 查找第一个<p>标签的位置，并保留其后面的所有内容
            match = re.search(r'<p', space_clear_html)
            if match:
                # 取从<p>开始到结束的所有内容
                cleared_data = space_clear_html[match.start():]
                return cleared_data
            else:
                # 如果没有找到<p>标签，返回原字符串或空字符串
                _log.info("拿到正文后，但第一个p标签没找到，返回空字符串")
                return ""


    #处理成文/发布日期：1.先查看文章里的日期是否存在，如果存在，并且与外面日期一样，则使用文章里面的。/如果不一样，则取文章里的日期。2.如果文章里无日期，则将外面的日期作为成文日期
    def extract_date_line(self,html_content,chengwen_time):
        # 定义日期模式
        date_pattern = re.compile(r'(\d{4}年\d{1,2}月\d{1,2}日)')

        # 按行分割字符串
        lines = html_content.split('\n')

        # 从后向前搜索包含日期的行
        for line in reversed(lines):
            match = date_pattern.search(line)
            if match:
                date = match.group(1)
                if date:
                    return date
                else:
                    return chengwen_time


    #处理实施日期，如果“起施行”前含有年月日，则取出年月日，如果“起施行”中不含有日期，则返回成文/发布日期
    def  shixing_date(self,html,faburiqi):
        if "起施行" not in html:
            _log.info(" 没有找到包含“起施行”,因此，发文/成文日期为施行日期")
            return faburiqi

        # 定义“起施行”模式
        effective_pattern = re.compile(r'.*?(\d{4}年\d{1,2}月\d{1,2}日).*?起施行',)

        # 按行分割字符串
        lines = html.split('\n')
        # 从后向前搜索包含“起施行”的行
        for line in reversed(lines):
            if "起施行" in line:
                match = effective_pattern.search(line)
                if match:
                    date = match.group(1)
                    _log.info("文中含有新的实施日期:", date)
                    return  date
                else:
                    # 行中有“起施行”但没有日期
                    _log.info("文中无新的实施日期，因此，发文/成文日期为施行日期")
                    return faburiqi

    #处理效力级别
    def level(self,name,title,clear_html,fazihao):
        if name in self.level_of_effectiveness.keys():
            return self.level_of_effectiveness[name]

        clean = re.compile('<.*?>')
        clean_tab_text = re.sub(clean, '', clear_html)
        if '规' in fazihao or '为贯彻落实' in title or '解释权' in clean_tab_text[-50:]:
            effectiveness_level = 'XP08'
            return effectiveness_level


    #处理唯一标识
    def md5_num(self,title,faburiqi):
        m = hashlib.md5()
        string=str(title)+str(faburiqi)
        m.update(string.encode('utf-8'))
        return m.hexdigest()

    #别人代码
    def a_href_calculate(self, soup, quanwen, title_any):
        """

        :param soup:
        :param quanwen:
        :param title_any:
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
        quanwen = str(quanwen)
        self.download_dt = download_dt
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

    #别人代码
    def query(self,list_name, ddd1, ddd2):
        query1 = {
            "query": {"bool": {
                "must": [{"match_phrase": {list_name: ddd1}},
                         {"match_phrase": {list_name: ddd2}}]}}}
        query2 = {"query": {"match": {list_name: ddd2}}}
        return [query1, query2]

    #别人代码
    def select(self,list_name, titl, chean_text, quer, fm):
        resp = es.search(index=['lar', 'chl'], body=quer)
        hits_total = resp["hits"]["hits"]
        z = 0
        for hits in hits_total:
            z += 1
            # print(hits)
            title = hits['_source']['标题']
            title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
            titl = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', titl)
            try:
                wenhao = hits['_source']['发文字号']
            except:
                wenhao = 'aaaaaaa'
            try:
                libb = hits['_source']['lib']
            except:
                libb = ''
            if wenhao:
                wenhao = wenhao
            else:
                wenhao = 'aaaaaaa'
            wenhao = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', wenhao)
            # print(chean_text,title)
            try:
                jigou = hits['_source']['发布部门']
            except:
                jigou = ''
            if jigou == '':
                if list_name == '标题':
                    a = (titl in title or title in titl)
                else:
                    a = (
                            chean_text in wenhao or wenhao in chean_text or titl in title or title in titl or 'chl' in libb)
            else:
                if list_name == '标题':
                    a = (titl in title or title in titl) and (fm in jigou or 'chl' in libb)
                else:
                    a = (chean_text in wenhao or wenhao in chean_text or titl in title or title in titl) and (
                            fm in jigou or 'chl' in libb)
            if a:
                return True
            elif z <= len(hits_total) and a:
                return True
            elif z < len(hits_total) and not a:
                pass
            else:
                return False

    #别人代码，用于判断新收录文件标题是否存在法器当中
    def check_existence(self,input_data, title, column, quer, fm):
        '''
        该函数用于判断新收录文件标题是否存在法器当中
        :param input_data: 新收录文件标题
        '''
        title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
        if '转发' not in title:
            chean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  # .split('关于')[-1]
        else:
            chean_text = title
        a = self.select(column, title, chean_text, quer, fm)
        if a:
            # print(rf'{input_data}存在于法器中')
            return True
        else:
            # print(rf'{input_data}不存在于法器中')
            return False

    def lar_esquc(self,title, column, issued_date=None):
        if '转发' not in title:
            clean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  # .split('关于')[-1]
        else:
            clean_text = title
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                column: {
                                    "query": clean_text,
                                    "slop": 0,
                                    "zero_terms_query": "NONE",
                                    "boost": 1.0
                                }
                            }
                        }
                    ]
                }
            }
        }
        resp = es.search(index='lar', body=body)
        list_a = resp['hits']['hits']
        if list_a:
            for it in list_a:
                title_real = it['_source'].get('标题')
                issued_date_real = it['_source'].get('发布日期')
                # 当标题等于传入标题的同时，如果有传入发布日期，那么就判断发布日期是否一致
                if title == title_real:
                    if issued_date:
                        if issued_date_real == issued_date:
                            return True
                    else:
                        return True
        else:
            return False

    ##查找es库中是否有这个数据
    def main_panduan(self,title_a, fm='831', ddd='重庆', issued_number=None, issued_date=None):
        """
        判断es数据库中是否已经有这个文章内容
        :param issued_date: 发布日期
        :param ddd:
        :param title_a:  标题
        :param fm: 文章来源地区编号（例如重庆市：831）
        :param issued_number: 发文字号
        :return:
        """
        chatitle = title_a
        query1 = self.query('标题', ddd, chatitle)[0]
        a = self.check_existence(title_a, title_a, '标题', query1, fm)
        if issued_number:
            query2 = self.query('发文字号', ddd, issued_number)[1]
            b = self.check_existence(issued_number, issued_number, '发文字号', query2, fm)
            if (self.lar_esquc(title_a, '标题', issued_date) or a) and title_a[-3:] != '...':
                return True
            else:
                if (self.lar_esquc(issued_number, '发文字号', issued_date) or b) and len(issued_number.strip()) > 2:
                    return True
            return False
        else:
            a = self.check_existence(title_a, title_a, '标题', query1, fm)
            if (self.lar_esquc(title_a, '标题', issued_date) or a) and title_a[-3:] != '...':
                return True
            return False



    #判断法器是否有这条数据
    @retry(stop_max_attempt_number=3)
    def process_row(self, title,fazihao,faburiqi):
        any_title = title
        any_issued_number = fazihao
        any_issued_date =faburiqi
        if self.main_panduan(any_title, issued_number=any_issued_number, issued_date=any_issued_date):   #查找es库中是否有这个数据
            _log.info(f"法器地方法规已有这条数据,无需抓取： {any_title}")
            return False
        _log.info(f"法器地方法规没有这条数据： {any_title}")
        return True


    #别人代码，附件下载函数
    def annex_get_all(self, issued_date, new_get_url):
        """
        附件下载函数
        :param issued_date: 发布日期
        :return:
        """
        download_dt = self.download_dt
        # 使用正则表达式匹配直到最后一个斜杠之前的路径
        pattern = r'^(https?://[^/]+/[^/]+)$'
        match = re.match(pattern, new_get_url)
        if match:
            # 如果匹配成功，返回匹配的部分
            new_get_url = match.group(0)
        if download_dt:
            for key, value in download_dt.items():
                if not issued_date:
                    continue
                try:
                    self.pf.annex_get(url=new_get_url, save_path=key, headers=self.headers,
                                      save_path_real=self.save_path_real)
                    _log.info(f"写入附件，标题为：{key} ,url为:{new_get_url}!!!")
                except Exception as e:
                    _log.info(f"annex_get_all发生错误：{e}")
        else:
            _log.info(f"没有附件内容需要写入！！！")

    #清洗拿到去除格式的正文，以及获取到其他字段
    def parile_content(self,url,title,fazihao,chengwen_time):
            response = requests.get(url, headers=self.headers)
            response.encoding = "utf-8"
            data_dt = {
                "html":response.text
            }
            space_clear_html = main_clean_cal(data_dt=data_dt)

            #已经清洗后的正文,去除开头一些标签
            clear_html=self.space_clear(str(space_clear_html))

            #处理成文/发布日期
            faburiqi =self.extract_date_line(clear_html,chengwen_time)

            #处理实施日期
            shishiriqi=self.shixing_date(clear_html,faburiqi)

            #处理效力级别
            name="地方规范性文件"
            xiaoli_level=self.level(name,title,clear_html,fazihao)

            #唯一标志，标题和发布时间的md5
            md5_text=self.md5_num(title,faburiqi)

            #发布部门
            fabubumen=self.pf.department(clear_html,title,area_num=self.area_num)  # 831:重庆地区

            #类别
            leibie=self.pf.catagroy_select(clear_html,title)

            #时效性
            shixiaoxing=self.shixiaoxing

            #附件
            clear_html = self.a_href_calculate(BeautifulSoup(clear_html,'html'), clear_html, title)
            # process_row用于二次检索该文章是否需要
            if self.process_row(title,fazihao,faburiqi):
                self.annex_get_all(faburiqi, url)

            # 创建字典
            data_dict = {
                '发布日期': faburiqi,
                '实施日期': shishiriqi,
                '效力级别': xiaoli_level,
                '唯一标志': md5_text,
                '发布部门': fabubumen,
                '类别': leibie,
                '时效性': shixiaoxing,
                '全文': clear_html,
                "法规标题":title,
                "来源":url
            }

            return data_dict

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

    def calcluate(self):
        for i in range(self.read_pages_start,self.num_pages):
            if i == 0:
                new_url = self.start_url
            else:
                new_url = self.start_url + f"index_{i}.html"

            #别人代码， 获取该页内容信息，就是主页面的一些信息，主页面的标题，发文字号，成文日期
            result_lt = self.title_data_get(url=new_url)
            _log.info(f"第{i + 1}页    获取到{len(result_lt)} 篇内容！！！")

            # 别人代码， 过滤已有的文章，判断es数据库中是否已经有这个文章内容
            new_result_lt = self.pf.filter(result_lt)
            if not new_result_lt:
                _log.info(f"第{i + 1}页    无内容需要写入！！！")
                continue
            _log.info(f"第{i + 1}页    需要写入的文章有 {len(new_result_lt)} 篇！！！")
            filtered_list = self.main(new_result_lt)
            if filtered_list:
                _log.info(f"第{i + 1}页    实际需要写入的文章有 {len(filtered_list)} 篇！！！")
                data_df = pd.DataFrame(filtered_list)
                if not data_df.empty:
                    self.pf.to_mysql(data_df, self.table_name)
                    _log.info(f"第{i + 1}页    {len(filtered_list)}篇文件写入完毕！！！")
                else:
                    _log.info(f"第{i + 1}页:   内容已经存在！")
            else:
                _log.info(f"第{i + 1}页:   内容已经存在！")


def main_test():
    data_dt = {
        "start_url": 'https://zfcxjw.cq.gov.cn/zwgk_166/zfxxgkmls/zcwj/xzgfxwj/',  # 访问路径
        "write_table_name": '专项补充收录',  # 写入数据库表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 8,  # 读取页码总数
        "save_path_real": '重庆市行政规范文件',  # 附件存放路径的文件名
        "lasy_department": '重庆市住房和城乡建设委员会',  # 在函数返回为空的时候指定发布部门
        "level_of_effectiveness": '地方工作文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
        "shixiaoxing":"01",
        "area_num":831    # 831:重庆地区
    }
    obj = MainCal(**data_dt)
    obj.calcluate()


if __name__ == '__main__':
    main_test()






#已有标题，全文，发布日期，效力级别，实施日期，发文字号，来源url,唯一标志,发布部门,类别,时效性，附件#faseheadlines



