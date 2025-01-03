import hashlib
import random
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from 预处理 import _remove_attrs, intaa, insertsql, selectsql, gettimestr
from 附件下载程序 import public_down

# 常量定义
CATEGORY = '“十三五”国家环境保护标准工作'
BASE_URL = 'http://www.mee.gov.cn/ywgz/fgbz/bz/sywbzgz/'
CENTER_URL = 'https://www.mee.gov.cn/gkml/'
DATE_CUTOFF = 20170101
OUTPUT_FILE_TEMPLATE = 'E:/JXdata/生态环境依法行政法律资源应用支持系统/卫生健康依法行政法律资源应用支持系统/{}_{}.xls'

def download_attachment(href, save_path):
    """下载附件并返回新的链接路径"""
    public_down(href, save_path)
    return f'/datafolder/{save_path}'


def get_md5(string):
    """
    计算md5值
    :param string:
    :return:
    """
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def process_li_element(li, base_url, category):
    """处理每个<li>元素，提取并保存数据"""
    dateop = intaa(li.find('span').text)
    title = li.find('a').text.strip('...')

    if dateop <= DATE_CUTOFF or selectsql(f"SELECT * FROM [dbo].[hb-环保局] WHERE [标题] LIKE '{title}%'"):
        return

    any_href = li.find('a')['href']
    any_href = any_href.replace("../", '').replace('ml/', '')
    if not any_href.startswith('http'):
        href = CENTER_URL + any_href[2:]  # 处理相对路径

    response = requests.get(href)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")

    ul = soup.find('ul')
    if ul:
        [s.extract() for s in ul('span')]
        div = ul.find_all('div')
        if div:
            title = div[0].text
            fbbm = div[3].text
            dateFb = div[4].text or dateop
            fwzh = div[5].text
        else:
            fbbm = '环境保护部'
            dateFb = ''
            fwzh = ''

    box = soup.find('div', class_='Custom_UnionStyle') or \
          soup.find('div', class_='neiright_JPZ_GK_CP') or \
          soup.find('div', class_='content_body_box')

    if box:
        box = _remove_attrs(box)
        for a in box.find_all('a', href=re.compile(r'.html')):
            a.replace_with(BeautifulSoup(f"<p>{a.text}</p>", 'html.parser'))

        attachments = []
        for a in box.find_all('a', href=re.compile(r'\.(pdf|docx?|xlsx?|rar|zip|jpe?g|png|gif|txt|7z|gz)$')):
            attachment_path = download_attachment(base_url + a['href'][2:],
                                                  f'E:/JXdata/生态环境依法行政法律资源应用支持系统/十三五国家环境保护标准工作/{a["href"][2:]}')
            a['href'] = attachment_path
            attachments.append(attachment_path)

        for img in box.find_all('img'):
            img_path = download_attachment(base_url + img['src'][2:],
                                           f'E:/JXdata/生态环境依法行政法律资源应用支持系统/十三五国家环境保护标准工作/{img["src"][2:]}')
            img['src'] = img_path
            attachments.append(img_path)

        content = '<div>' + ''.join(str(tag) for tag in box) + '</div>'
        unique_id = get_md5(title)
        attachments_str = str(attachments).replace("'", '"')
        data_dict = {
            "标题": title,
            "类别": CATEGORY,
            "发布部门": fbbm,
            "发文字号": fwzh,
            "发布日期": dateFb,
            "实施日期": dateFb,
            "全文": content,
            "url": href,
            "附件": attachments_str,
            "唯一标志": unique_id
        }
        insertsql(
            "INSERT INTO [自收录数据].[dbo].[hb-环保局] ([标题], [类别], [发文字号],[发布部门], [发布日期], [实施日期], [全文], [url],[附件],[唯一标志]) VALUES "
            f"('{title}', '{category}', '{fwzh}', '{fbbm}', '{intaa(dateFb)}', '{dateop}', '{content}', '{href}', '{attachments_str}', '{unique_id}')"
        )
        return data_dict


def scrape_page(url, category):
    """抓取单页内容并处理"""
    data_lt = []
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find('ul', id="div")
    if ul:
        lis = ul.find_all('li')
        for li in lis:
            data_dt = process_li_element(li, url, category)
            if data_dt:
                data_lt.append(data_dt)
    return data_lt


def main():
    timem = time.strftime('%Y%m%d%H%M', time.localtime())
    for page in range(1):  # 抓取第一页和第二页
        url = BASE_URL if page == 0 else f"{BASE_URL}index_{page}.shtml"
        data_lt = scrape_page(url, CATEGORY)
        if data_lt:
            data_df = pd.DataFrame(data_lt)
            file_path = OUTPUT_FILE_TEMPLATE.format(CATEGORY, timem)
            data_df.to_excel(file_path, index=False)
            print(f"文件已经写入到[{file_path}]")


if __name__ == "__main__":
    main()
