import json
import os
import time
import random
from NewLawsGet.GetTitleUrl import ES_CLIENT
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import requests
from ProcessingMethod.GetAuthorization import calculate as get_new_authorization
import pandas as pd
from ProcessingMethod.LoggerSet import logger


class PaiCha:
    def __init__(self):
        self.proxies = dict(http='http://183.159.204.186:10344', https='http://183.159.204.186:10344')
        self.proxies_url = "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=b9200c80d01ddc746e97430b3d4a46a9&orderNo=GL202403191725045jqovn7t&count=1&isTxt=0&proxyType=1&returnAccount=1"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1717379125; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1717558686; JSESSIONID=12C7E253ECC5428DA27CC601E5DD0C62'
        }
        pass

    def get_new_proxies(self):
        """
        获取更新可用代理IP
        :return:
        """
        max_retries = 3
        while max_retries > 0:
            try:
                response = requests.get(self.proxies_url, headers=self.headers, timeout=15)
                data_js = response.json()
                proxie_dt = data_js.get('obj')[0]
                proxies_ip = proxie_dt.get('ip')
                proxies_port = proxie_dt.get('port')
                ip = f'http://{proxies_ip}:{proxies_port}'
                self.proxies = dict(http=ip, https=ip)
                print("代理更换完毕!")
                break
            except Exception as e:
                max_retries -= 1
                print(f"[proxies] 剩余重试次数:[{max_retries}],错误: {e}")
                time.sleep(random.uniform(1, 2))
                continue

    def loading_authorization(self):
        # 获取脚本所在的绝对路径
        script_directory = os.path.dirname(os.path.abspath(__file__))
        # 构建目标目录的相对路径
        config_directory = os.path.join(script_directory, 'ConfigFile')
        # 构建文件的绝对路径
        file_path = os.path.join(config_directory, 'authorization.txt')
        with open(file_path, 'r') as ac:
            authorization = ac.read().replace('"', "")
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/json',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'authorization': authorization
        }
        return headers

    def create_form_data(self, page_index):
        """
        创建用于发送请求的表单数据。
        适用于 法律法规
        参数:
        page_index (int): 当前页面索引。

        返回:
        dict: 表单数据字典。
        """

        previous_index = page_index - 1
        if previous_index < 0:
            previous_index = 0

        form_data = {
            "orderbyExpression": "IkBoost Desc,IssueDate Asc,TitleBoost Desc,EffectivenessSort Asc,IsOriginal Desc,DocumentNOSort Desc",
            "pageIndex": page_index,
            "pageSize": 100,
            "fieldNodes": [
                {
                    "type": "select",
                    "order": 2,
                    "showText": "制定机关",
                    "fieldName": "IssueDepartment",
                    "combineAs": 2,
                    "fieldItems": [
                        {
                            "value": [
                                "5",
                                "60322"
                            ],
                            "keywordTagData": [
                                "5",
                                "6/603/60322"
                            ],
                            "order": 0,
                            "combineAs": 2,
                            "items": [
                                {
                                    "value": "5",
                                    "name": "国务院",
                                    "text": "国务院",
                                    "path": "5"
                                },
                                {
                                    "value": "60322",
                                    "name": "中国银行保险监督管理委员会(已撤销)",
                                    "text": "国务院各机构/各委/中国银行保险监督管理委员会(已撤销)",
                                    "path": "6/603/60322"
                                }
                            ],
                            "filterNodes": []
                        }
                    ]
                },
                {
                    "type": "daterange",
                    "order": 3,
                    "showText": "公布日期",
                    "fieldName": "IssueDate",
                    "combineAs": 2,
                    "range": "",
                    "fieldItems": [
                        {
                            "order": 0,
                            "combineAs": 1,
                            "start": "2010.01.01",
                            "end": "2015.10.01"
                        }
                    ]
                }
            ],
            "clusterFilters": {},
            "groupBy": {}
        }

        return form_data

    def test_ip(self, proxy):
        try:
            response = requests.get('https://www.example.com', proxies=proxy, timeout=5)
            print("代理生效!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"{proxy} 代理已失效!")
            return False

    def make_request(self, params_data):
        """
        发送 POST 请求并返回响应文本。

        参数:
        page_index (int): 当前页面页数。
        params_data (dict): 请求参数数据。

        返回:
        str: 响应文本。
        """
        url = 'https://www.pkulaw.com/searchingapi/adv/list/chl'
        max_retries = 5  # 最大重试次数
        retry_delay = random.uniform(2, 3)  # 重试之间的延迟时间（秒）
        error_num = 0
        # 重试逻辑
        for attempt in range(max_retries):
            # 记录日志
            logger.info(f"等待 {retry_delay:.2f} 秒后再发起请求。")
            time.sleep(retry_delay)
            try:
                if not self.test_ip(self.proxies):
                    # 更换代理
                    self.get_new_proxies()
                headers = self.loading_authorization()  # 加载授权信息
                response = requests.post(url, json=params_data, headers=headers, proxies=self.proxies)
                logger.info(f'连接状态<{response.status_code}>')

                # 如果请求成功
                if response.status_code == 200:
                    return response.text
                else:
                    error_num += 1
                    if error_num > 2 or response.status_code == 401:
                        logger.info("尝试获取新的授权信息")
                        # 如果请求不成功，尝试获取新的授权信息
                        get_new_authorization()
                        error_num = 0
            except requests.RequestException as e:
                # 记录网络请求异常
                logger.error(f'请求过程中发生错误: {e}')

            # 如果不是最后一次尝试，记录重试信息
            if attempt < max_retries - 1:
                logger.warning(f'请求失败，正在进行第 {attempt + 1}/{max_retries} 次重试。')
                time.sleep(retry_delay)

        # 如果达到最大重试次数仍未成功，记录错误并返回 None
        logger.error('达到最大重试次数，请求失败。')
        return None

    def extract_titles_and_urls(self, content_json):
        """
        从网页内容中提取标题和 URL。适用于法律法规

        参数:
        content (str): 网页内容。

        返回:
        tuple: 包含状态 ('end' 或 'continue') 和标题与 URL 字典的元组。
        """
        new_data_lt = []
        # 将JSON字符串转换为字典
        data_dict_all = json.loads(content_json)
        data_lt = data_dict_all.get('data')
        for it in data_lt:
            title = it.get('title')
            enggid = it.get('enggid')
            summaries = it.get('summaries')
            fawen = summaries[1].get('text')
            if "公布" in fawen:
                fawen = ""
            data_dt = {
                "标题": title,
                "链接": f"/chl/{enggid}.html?way=listView",
                "发文字号": fawen
            }
            new_data_lt.append(data_dt)
        data_df = pd.DataFrame(new_data_lt)
        return data_df

    def check_elasticsearch_existence(title, index):
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
        response = ES_CLIENT.search(index=index, body=query_body)
        if int(response['hits']['total']) == 0:
            # print(f'文章不存在: {title}')
            return True
        else:
            # print(f'存在文章: {title}')
            return False

    def get_title_url(self):
        """
        获取所有页面上的标题和URL，并返回一个包含这些信息的DataFrame。

        参数:
        create_form_data (callable): 创建表单数据的函数。
        make_request (callable): 发送请求并返回响应内容的函数。
        extract_titles_and_urls (callable): 从响应内容中提取标题和URL的函数。

        返回:
        DataFrame: 包含所有页面的标题和URL的数据框。
        """
        current_page = 0
        # 获取总页数
        initial_content = self.make_request(params_data=self.create_form_data(current_page))
        initial_data_dict = json.loads(initial_content)
        total_pages = (initial_data_dict.get('sum', 0) // 100) + 1
        logger.info(f"一共{total_pages}页!")
        # 提取第一页的数据
        all_data_df = self.extract_titles_and_urls(initial_content)

        # 循环获取剩余页面的数据
        for current_page in range(1, total_pages):
            logger.info(f"正在获取第{current_page + 1}页!")
            page_content = self.make_request(params_data=self.create_form_data(current_page))
            if page_content:
                page_data_df = self.extract_titles_and_urls(page_content)
                all_data_df = pd.concat([all_data_df, page_data_df], ignore_index=True)

        return all_data_df

    def save_to_excel(self, dataframe, filename):
        """
        保存DataFrame到Excel文件
        """
        with pd.ExcelWriter(filename) as writer:
            dataframe.to_excel(writer, startrow=0, startcol=0)
        print(f"{filename} 写入完毕！！！")

    def calculate(self, choose=True):
        # 收录内容
        all_data_df = self.get_title_url()
        return False


if __name__ == '__main__':
    obj = PaiCha()
    obj.calculate()
