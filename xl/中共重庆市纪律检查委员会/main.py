# coding:utf-8
import random
import re

import pandas as pd
import requests
from botpy import logging
from elasticsearch import Elasticsearch
import time
from datetime import datetime
from query import PublicFunction
from lxml import html, etree
_log = logging.get_logger()
from xl.中共重庆市纪律检查委员会.clear_content import  main_test as main_clean_cal
import hashlib



class MainCal:
        def __init__(self, **kwargs):
            self.shouludate = "XL" + str(datetime.now().strftime("%Y.%m.%d"))
            self.pf = PublicFunction
            # # 读取页数
            # self.num_pages = kwargs.get("read_pages_num")
            # 写入表名
            self.table_name = kwargs.get("write_table_name")
            # 存放路径
            self.save_path_real = kwargs.get("save_path_real")
            # 初始url
            self.start_url = kwargs.get("start_url")
            # 请求头
            self.headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "max-age=0",
                "priority": "u=0, i",
                "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "none",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

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
                "重庆市住房和城乡建设委员会":"8;831;83103;831030467",
                "重庆市农业农村委员会":"8;831;83103;831030035",
                "重庆市退役军人事务局":"8;831;83103;831030038",
                "重庆市城市管理局":"8;831;83103;831030466",
                "重庆市商务委":"8;831;83103;831030402",
                "重庆市应急管理局":"8;831;83103;831030037",
                "重庆市交通运输委":"8;831;83103;831030015",
                "重庆市文化旅游委":"8;831;83103;831030040",
                "重庆市审计局":"8;831;83103;831030242",
                "重庆市水利局":"8;831;83103;831030016",
                "重庆市卫生健康委":"8;831;83103;831030039",
                "重庆市政府外办":"8;831;83103;831030232",
                "中共重庆市纪律检查委员会":"8;831;83103;831030163"

            }
            # 在函数返回为空的时候指定发布部门
            self.lasy_department = self.department_of_publication.get(kwargs.get('lasy_department'))
            # 收录来源个人
            self.myself_mark = kwargs.get("lasy_department")
            # 部门
            self.level_of_effectiveness_real = self.level_of_effectiveness.get(kwargs.get("level_of_effectiveness"))
            # # 指定起始页数
            # self.read_pages_start = kwargs.get('read_pages_start')
            # if not self.read_pages_start:
            #     self.read_pages_start = 0
            self.pf = PublicFunction
            self.download_dt = {}
            self.shixiaoxing=kwargs.get("shixiaoxing")
            self.area_num=kwargs.get("area_num")

        #得到主页面的所有href
        def main(self,new_resul):
            filter_lt = []
            for i in new_resul:
                url = i['法规url']

                title = i['法规标题']
                chengwen_time = i['发布日期']
                data_dict = self.parile_content(url, title,chengwen_time)
                if data_dict == "stop":
                    filter_lt.append(data_dict)
                else:
                    filter_lt.append(data_dict)

            return filter_lt

        # 清洗开头，从<p标签开始之后都拿到，如果没有找到<p>标签，返回原字符串或空字符串
        def space_clear(self, space_clear_html):
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

        def level(self, name, title, clear_html):
            if name in self.level_of_effectiveness.keys():
                return self.level_of_effectiveness[name]

            clean = re.compile('<.*?>')
            clean_tab_text = re.sub(clean, '', clear_html)
            if  '为贯彻落实' in title or '解释权' in clean_tab_text[-50:]:
                effectiveness_level = 'XP08'
                return effectiveness_level

        def md5_num(self, title, faburiqi):
            m = hashlib.md5()
            string = str(title) + str(faburiqi)
            m.update(string.encode('utf-8'))
            return m.hexdigest()


        def parile_content(self, url, title,chengwen_time):
            response = requests.get(url, headers=self.headers)
            response.encoding = "utf-8"
            data_dt = {
                "html": response.text,
                "title": title
            }

            time.sleep(random.randint(1, 3))
            space_clear_html = main_clean_cal(data_dt=data_dt)
            time.sleep(0.5)

            # 已经清洗后的正文,去除开头一些标签
            clear_html = self.space_clear(str(space_clear_html))
            time.sleep(0.5)

            # 处理效力级别
            name = "地方工作文件"
            xiaoli_level = self.level(name, title, clear_html)
            time.sleep(0.5)


            #处理发布部门
            fabubumen="8;831;83102"

            #类别
            leibie="003;00301"

            #时效性
            shixiaoxing=self.shixiaoxing

            #发布日期
            faburiqi=chengwen_time
            faburiqi = faburiqi.replace('-', '.')

            #实施日期
            shishiriqi=chengwen_time
            shishiriqi =shishiriqi.replace('-', '.')


            # 唯一标志，标题和发布时间的md5
            md5_text = self.md5_num(title, faburiqi)
            time.sleep(0.5)


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
                "法规标题": title,
                "来源": url,
                "发文字号": '',
                "收录时间": self.shouludate
            }

            return data_dict



        def fetch_url(self,url):
            results=[]
            cl_num = 3
            for it in range(cl_num):
                try:
                    sleep = random.uniform(0, 2)
                    _log.info(f"休眠{sleep}秒")
                    time.sleep(sleep)
                    # 发送 HTTP GET 请求
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        # 返回页面内容
                        # soup = BeautifulSoup(response.content, 'html.parser')
                        tree = etree.HTML(response.content)
                        div_list = tree.xpath('//div[@id="list"]//ul/li')
                        for div in div_list:
                             if div.xpath('./h1/a/text()')!=['在新的赶考路上坚持不懈正风肃纪反腐', '为书写重庆全面建设社会主义现代化新篇章提供坚强保障']:
                                title=div.xpath('./h1/a/text()')[0]
                                href =div.xpath('./h1/a/@href')[0]
                                fabushijian=div.xpath('./div/text()')[0]
                                results.append({'title': title, 'href': href,"ftimel":fabushijian})
                        return results

                    else:
                        # 如果状态码不是200，则尝试修改URL并重新请求
                        _log.info(f"请求失败，状态码：{response.status_code}")
                except requests.exceptions.RequestException as e:
                    _log.info(f"出错！      {e}")
                    sleep = random.uniform(2, 4)
                    _log.info(f"休眠{sleep}秒")
                    time.sleep(sleep)
                    _log.info("==========================")

            _log.info("达到最大重试次数，仍无法获取该网站内容")
            _log.info(f"网站url:  {url}")
            return None



        def title_data_get(self, url):
            """
            用于获取到总页面内容，获取到该页的 标，发文字号，成文日期
            :return:result_lt：列表套字典，字典装有信息
            """
            # result_lt = []
            resuluts = self.fetch_url(url=url)
            # 初始化一个空列表来存储转换后的数据
            converted_data = []

            # 遍历原始数据列表
            for item in resuluts:
                # 创建一个新的字典并填充数据
                new_item = {
                    "法规标题": item['title'],
                    "法规url": item['href'],
                    "发布日期":item['ftimel']
                }
                # 将新字典添加到转换后的数据列表中
                converted_data.append(new_item)
            # print(converted_data)
            return converted_data


        def calcluate(self):
                # 别人代码， 获取该页内容信息，就是主页面的一些信息，主页面的标题，发文字号，成文日期
                resuluts=self.title_data_get(url=self.start_url)
                _log.info(f"获取到{len(resuluts)} 篇内容！！！")
                #
                new_result_lt = self.pf.filter(resuluts)
                if not new_result_lt:
                    _log.info(f"  无内容需要写入！！！")
                else:
                    _log.info(f"需要写入的文章有 {len(new_result_lt)} 篇！！！,已经过滤了es库")
                    filtered_list = self.main(new_result_lt)
                    if filtered_list == "stop":
                        _log.info(f" 这条数据跳过了！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！！要重新查看")
                    elif filtered_list:
                        _log.info(f"  实际需要写入的文章有 {len(filtered_list)} 篇！！！")
                        data_df = pd.DataFrame(filtered_list)
                        if not data_df.empty:
                            if not "stop" in filtered_list:
                                self.pf.to_mysql(data_df, self.table_name)
                                _log.info(f" {len(filtered_list)}篇文件写入完毕！！！")
                        else:
                            _log.info(f"内容已经存在！")
                    else:
                        _log.info(f"内容已经存在！")







def main_test():
    data_dt = {
        "start_url": "https://jjc.cq.gov.cn/html/col609191.htm",# 访问路径
        "write_table_name": '中共重庆市收录',  # 写入数据库表名
        # 'read_pages_start': 0,  # 读取页码起始数(调试用)
        # "read_pages_num": 9,  # 读取页码总数
        "save_path_real": '中共重庆市纪律检查',  # 附件存放路径的文件名
        "lasy_department": '中共重庆市纪律检查委员会',  # 在函数返回为空的时候指定发布部门
        "level_of_effectiveness": '地方工作文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
        "shixiaoxing":"01",
        "area_num":831    # 831:重庆地区
    }
    obj = MainCal(**data_dt)
    obj.calcluate()


if __name__ == '__main__':
    main_test()
