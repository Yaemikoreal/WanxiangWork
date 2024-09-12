# coding:utf-8
import re

import requests
from lxml import etree
from test_content import  main_test as main_clean_cal
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36", }

#得到主页面的所有href
def main():
    url = 'https://sjj.cq.gov.cn/zwgk/zcwj/ghxwj/'
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    tree=etree.HTML(response.text)
    tr_list=tree.xpath('//td[@class="title"]//a')
    href_list=[]
    for tr in tr_list:
        title=tr.xpath('./p/text()')[0]
        href='https://sjj.cq.gov.cn/zwgk/zcwj/ghxwj'+tr.xpath('./@href')[0].replace('./','/')
        href_list.append(href)
    parile_content(href_list)

#清洗开头，从<p标签开始之后都拿到
def space_clear(space_clear_html):
        # 查找第一个<p>标签的位置，并保留其后面的所有内容
        match = re.search(r'<p', space_clear_html)
        if match:
            # 取从<p>开始到结束的所有内容
            cleared_data = space_clear_html[match.start():]
            return cleared_data
        else:
            # 如果没有找到<p>标签，返回原字符串或空字符串
            return ""


def parile_content(href_list):
    for i in href_list:
        # i='https://sjj.cq.gov.cn/zwgk/zcwj/ghxwj/202401/t20240110_12807660.html'
        response = requests.get(i, headers=headers)
        response.encoding = "utf-8"
        data_dt = {
            "html":response.text
        }
        space_clear_html = main_clean_cal(data_dt=data_dt)
        clear_html=space_clear(str(space_clear_html))
        print(clear_html)
        print("-"*200)



if __name__ == '__main__':
    main()