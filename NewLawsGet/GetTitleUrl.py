import time
import random
from ProcessingMethod.LoggerSet import logger
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
import requests
import re
import pandas as pd
from GetTitleCookie import calculate as get_url_headers

"""
该方法用于自动获取法宝新法速递标题和url信息

注意:运行该方法前，先启动NewInterface脚本！！！
为True时处理法律法规新内容，为False时处理地方法规内容
输出内容存在于:附件/chl.xlsx 和 附件/lar.xlsx 中.
"""

# 代理配置
PROXY = '127.0.0.1:1080'
PROXIES = {
    'http': f'socks5://{PROXY}',
    'https': f'socks5://{PROXY}'
}

# Elasticsearch 配置
ES_CLIENT = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


class GetTitleUrl:
    def __init__(self):
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "connection": "keep-alive",
            "content-length": "794",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": "referer=https://www.pkulaw.com/; _bl_uid=8tmqq2CO93Uw9bta8bjwdFIemC45; sensorsdata2015jssdkcross=%7B%22%24device_id%22%3A%22192e6e8033463-09f2438d266e14-4c657b58-1327104-192e6e803353a1%22%7D; chlOrderMemery=0; Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2206%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%220b1ef4c1-c209-ed11-b392-00155d3c0709%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D; xCloseNew=13; pkulaw_v6_sessionid=xf1fbviavvbkwth4zjgxf1x3; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1729473999,1730683927,1731289225,1731381388; HMACCOUNT=C1E3DEC5C46B85EE; cookieUUID=cookieUUID_1731381388301; WEIXIN_APP_LOGIN_KEY=fa56a43f-c1a3-4eae-a93c-434b21da34f7; __tst_status=905933405#; referer=https://www.pkulaw.com/; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1731401984",
            "host": "www.pkulaw.com",
            "origin": "https://www.pkulaw.com",
            "referer": "https://www.pkulaw.com/",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "x-requested-with": "XMLHttpRequest"
        }
        self.local_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "connection": "keep-alive",
            "content-length": "794",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "cookie": "referer=https://www.pkulaw.com/; _bl_uid=8tmqq2CO93Uw9bta8bjwdFIemC45; sensorsdata2015jssdkcross=%7B%22%24device_id%22%3A%22192e6e8033463-09f2438d266e14-4c657b58-1327104-192e6e803353a1%22%7D; chlOrderMemery=0; Hm_up_8266968662c086f34b2a3e2ae9014bf8=%7B%22ysx_yhqx_20220602%22%3A%7B%22value%22%3A%220%22%2C%22scope%22%3A1%7D%2C%22ysx_hy_20220527%22%3A%7B%22value%22%3A%2206%22%2C%22scope%22%3A1%7D%2C%22uid_%22%3A%7B%22value%22%3A%220b1ef4c1-c209-ed11-b392-00155d3c0709%22%2C%22scope%22%3A1%7D%2C%22ysx_yhjs_20220602%22%3A%7B%22value%22%3A%221%22%2C%22scope%22%3A1%7D%7D; xCloseNew=13; pkulaw_v6_sessionid=xf1fbviavvbkwth4zjgxf1x3; Hm_lvt_8266968662c086f34b2a3e2ae9014bf8=1729473999,1730683927,1731289225,1731381388; HMACCOUNT=C1E3DEC5C46B85EE; cookieUUID=cookieUUID_1731381388301; WEIXIN_APP_LOGIN_KEY=fa56a43f-c1a3-4eae-a93c-434b21da34f7; __tst_status=905933405#; referer=https://www.pkulaw.com/; Hm_lpvt_8266968662c086f34b2a3e2ae9014bf8=1731401984",
            "host": "www.pkulaw.com",
            "origin": "https://www.pkulaw.com",
            "referer": "https://www.pkulaw.com/",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
            "x-requested-with": "XMLHttpRequest"
        }

    def save_to_excel(self, dataframe, filename):
        """保存DataFrame到Excel文件"""
        with pd.ExcelWriter(filename) as writer:
            dataframe.to_excel(writer, startrow=0, startcol=0)
        logger.info(f"{filename} 写入完毕！！！")

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
        response = ES_CLIENT.search(index=index, body=query_body)
        if int(response['hits']['total']) == 0:
            # logger.info(f'文章不存在: {title}')
            return True
        else:
            logger.info(f'ES存在文章: {title}')
            return False

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
            "Menu": "law",
            "Keywords": "",
            "SearchKeywordType": "Title",
            "MatchType": "Exact",
            "RangeType": "Piece",
            "Library": "chl",
            "ClassFlag": "chl",
            "GroupLibraries": "",
            "QueryOnClick": False,
            "AfterSearch": False,
            "PreviousLib": "chl",
            "pdfStr": "",
            "pdfTitle": "",
            "IsSynonymSearch": False,
            "RequestFrom": "",
            "LastLibForChangeColumn": "chl",
            "IsSearchProvision": False,
            "IsCustomSortSearch": False,
            "CustomSortExpression": "",
            "IsAdv": False,
            "ClassCodeKey": ",,,,,,",
            "Aggs.RelatedPrompted": "01",
            "Aggs.EffectivenessDic": "",
            "Aggs.SpecialType": "",
            "Aggs.IssueDepartment": "",
            "Aggs.TimelinessDic": "",
            "Aggs.Category": "",
            "Aggs.IssueDate": "",
            "GroupByIndex": "2",
            "OrderByIndex": "0",
            "ShowType": "Default",
            "GroupValue": "",
            "TitleKeywords": "",
            "FullTextKeywords": "",
            "Pager.PageIndex": page_index,
            "RecordShowType": "List",
            "Pager.PageSize": "100",
            "QueryBase64Request": "",
            "VerifyCodeResult": "",
            "isEng": "chinese",
            "OldPageIndex": previous_index,
            "newPageIndex": "",
            "IsShowListSummary": "",
            "X-Requested-With": "XMLHttpRequest"
        }
        return form_data

    def create_form_data_local(self, page_index):
        """
        创建用于发送请求的表单数据。
        适用于 地方法规
        参数:
        page_index (int): 当前页面索引。

        返回:
        dict: 表单数据字典。
        """
        previous_index = page_index - 1
        if previous_index < 0:
            previous_index = 0
        form_data = {
            'Menu': 'law',
            'Keywords': '',
            'SearchKeywordType': 'Title',
            'MatchType': 'Exact',
            'RangeType': 'Piece',
            'Library': 'lar',
            'ClassFlag': 'lar',
            'GroupLibraries': '',
            'QueryOnClick': False,
            'AfterSearch': False,
            'PreviousLib': 'lar',
            'pdfStr': '',
            'pdfTitle': '',
            'IsSynonymSearch': False,
            'RequestFrom': 'btnSearch',
            'LastLibForChangeColumn': 'lar',
            'IsSearchProvision': 'False',
            'IsCustomSortSearch': 'False',
            'CustomSortExpression': '',
            'IsAdv': False,
            'ClassCodeKey': ',,,,,,',
            'Aggs.RelatedPrompted': '01',
            'Aggs.EffectivenessDic': '',
            'Aggs.SpecialType': '',
            'Aggs.IssueDepartment': '',
            'Aggs.TimelinessDic': '',
            'Aggs.Category': '',
            'Aggs.IssueDate': '',
            'GroupByIndex': '2',
            'OrderByIndex': '0',
            'ShowType': 'Default',
            'GroupValue': '',
            'TitleKeywords': '',
            'FullTextKeywords': '',
            'Pager.PageIndex': page_index,
            'RecordShowType': 'List',
            'Pager.PageSize': '100',
            'QueryBase64Request': '',
            'VerifyCodeResult': '',
            'isEng': 'chinese',
            'OldPageIndex': previous_index,
            'newPageIndex': '',
            'IsShowListSummary': '',
            'X-Requested-With': 'XMLHttpRequest'
        }
        return form_data

    def make_request(self, page_index, choose, new_headers):
        """
        发送 POST 请求并返回响应文本。

        参数:
        page_index (int): 当前页面索引。
        choose(bool): 为True时处理法律法规新内容，为False时处理地方法规内容
        返回:
        str: 响应文本。
        """
        url = 'https://www.pkulaw.com/law/search/RecordSearch'
        try_num = 5
        while try_num > 0:
            time.sleep(random.uniform(2, 4))
            if choose:
                params_data = self.create_form_data(page_index)
            else:
                params_data = self.create_form_data_local(page_index)
            try:
                response = requests.post(url, data=params_data, verify=False, headers=new_headers)
                logger.info(f'连接状态<{response.status_code}>')
                response_text = response.text
                if "<script>var " in response_text:
                    logger.info("获取内容不符，重试~")
                    try_num -= 1
                    continue
                return response_text
            except Exception as e:
                logger.error(f'错误: {e}')
                try_num -= 1

    def extract_titles_and_urls(self, content):
        """
        从网页内容中提取标题和 URL。适用于法律法规

        参数:
        content (str): 网页内容。

        返回:
        tuple: 包含状态 ('end' 或 'continue') 和标题与 URL 字典的元组。
        """
        pattern = re.compile(
            r'<a bdclick logfunc="文章点击" logplace="右侧列表" logplate="列表" logother=".*?" target="_blank" flink="true" href="(?P<url>.*?)">(?P<title>.*?)</a>',
            re.S)
        matches = pattern.finditer(content)
        titles_and_urls = {match.group('title'): match.group('url') for match in matches}

        if not titles_and_urls:
            logger.info('获取标题与URL数据内容为空！！！')
            return 'end', {}

        logger.info(titles_and_urls)
        return 'continue', titles_and_urls

    def extract_titles_and_urls_local(self, content):
        """
        从网页内容中提取标题和 URL。适用于地方法规

        参数:
        content (str): 网页内容。

        返回:
        tuple: 包含状态 ('end' 或 'continue') 和标题与 URL 字典的元组。
        """
        titles_and_urls = {}
        soup = BeautifulSoup(content, 'html.parser')
        title_url_soup = soup.find_all('a', target='_blank', flink='true')
        for tag in title_url_soup:
            title = tag.get_text()
            if title:
                url = tag.get('href')
                titles_and_urls[title] = url

        if not titles_and_urls:
            logger.info('获取标题与URL数据内容为空！！！')
            return 'end', {}

        logger.info(titles_and_urls)
        return 'continue', titles_and_urls

    def remove_unwanted_titles(self, titles_and_urls):
        """
        移除不需要的文章标题。

        参数:
        titles_and_urls (dict): 标题与 URL 的字典。

        返回:
        dict: 过滤后的标题与 URL 字典。
        """
        unwanted_keywords = [
            '免职通知', '免职的通知', '放假通知', '任职通知', '任职的通知', '比赛通知', '放假的通知',
            '同志退休', '同志任免职的通知', '同志晋升职级的通知', '同志免职', '同志任职的通知',
            '同志工作安排的通知', '年春节放假的通知', '赛的通知', '同志退休', '同志职务调整的通知',
            '同志任职的决定', '职务任免的通知', '工作职务的通知', '同志工作调整的通知', '邀请函',
            '晋升通知', '晋升的通知', '晋升职级的通知', '退休的通知', '任用的通知', '同志职务变动的通知',
            '任免职务的通知', '套转职级的通知', '公开赛', '任职资格的批复', '击剑'
        ]
        filtered_titles_and_urls = {}
        if titles_and_urls is None:
            return filtered_titles_and_urls
        for title, url in titles_and_urls.items():
            if not any(keyword in title for keyword in unwanted_keywords):
                filtered_titles_and_urls[title] = url

        logger.info(f'一共获取到 {len(filtered_titles_and_urls)} 篇有效文章!!!')
        return filtered_titles_and_urls

    def get_title_url(self, page_index, choose):
        try_num = 2
        index = 'chl' if choose else 'lar'
        logger.info(f"正在收录: {index} 内容")
        needed_content = {}
        while True:
            # 发送 POST 请求并返回响应文本
            content = self.make_request(page_index, choose, new_headers=self.headers)
            if not content:
                logger.info("未能获取到内容，重试!")
                try_num -= 1
                if try_num <= 0:
                    logger.info("正在更换cookie!!!")
                    new_headers = get_url_headers()
                    if not new_headers:
                        logger.info("更换失败!!!")
                        continue
                    self.headers = new_headers
                    logger.info("更换完毕，重试!!!")
                continue
            if choose:
                # 从网页内容中提取标题和 URL
                state, titles_and_urls = self.extract_titles_and_urls(content)
            else:
                state, titles_and_urls = self.extract_titles_and_urls_local(content)
            logger.info(f"从第 {page_index + 1} 页获取到了 {len(titles_and_urls)} 篇文章!!!")
            if state == 'continue':
                logger.info(f"正在获取第 {page_index + 1} 页内容!!!")
                for title, url in titles_and_urls.items():
                    # 检查 Elasticsearch 中是否存在给定标题的文章。
                    if self.check_elasticsearch_existence(title, index):
                        if not needed_content.get(title):
                            logger.info(f"添加标题:{title}  {url}")
                            needed_content[title] = url
                if page_index >= 25:
                    logger.info("获取完毕!!!")
                    return needed_content
            else:
                logger.info("获取失败!!!(或已经获取完毕)")
                return needed_content
            page_index += 1

    # 主程序
    def calculate(self, choose=True):
        # 页数
        page_index = 0
        # 收录内容
        needed_content = self.get_title_url(page_index, choose)
        # 移除不需要的文章标题
        final_content = self.remove_unwanted_titles(needed_content)

        if final_content:
            df = pd.DataFrame.from_dict(final_content, orient='index', columns=['链接'])
            df.index.name = '标题'
            filename = '附件/chl.xlsx' if choose else '附件/lar.xlsx'
            self.save_to_excel(df, filename)
            return True
        return False


if __name__ == '__main__':
    obj = GetTitleUrl()
    # choose(bool): 为True时处理法律法规新内容，为False时处理地方法规内容
    obj.calculate(choose=False)
