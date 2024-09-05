import hashlib
import random
import re
import time
from bs4 import BeautifulSoup,NavigableString
from lxml import etree
import requests
# -*- coding: utf-8 -*-

import time

import requests
import os

import pyodbc
import datetime
import re

import 类别判断
from 公司1.分类 import catagroy_select
from 公司1.附件下载程序 import public_down
from elasticsearch import Elasticsearch
import warnings
# import sys
# sys.path.append('/公司1/类别判断')
# sys.path.append('/公司1/分类')
# 忽略 MarkupResemblesLocatorWarning 警告
warnings.simplefilter('ignore')
es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)

def check_existence(input_data, title, column, quer, fm):
    '''
    该函数用于判断新收录文件标题是否存在法器当中
    :param input_data: 新收录文件标题
    '''
    titl = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
    if '转发' not in title:
        chean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)#.split('关于')[-1]
    else:chean_text=title
    a = select(column, title, chean_text, quer, fm)
    if a:
        # print(rf'{input_data}存在于法器中')
        return True
    else:
        # print(rf'{input_data}不存在于法器中')
        return False

def select(list_name, titl, chean_text, quer, fm):
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


def camptime(t, z):
    # 将输入日期字符串转换为 datetime 对象
    date_object = datetime.datetime.strptime(t, z)
    # 将日期对象转换为目标格式的字符串
    formatted_date = date_object.strftime("%Y.%m.%d")
    return formatted_date

def chl_esquc(title, column):
    if '转发' not in title:
        chean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)#.split('关于')[-1]
    else:chean_text=title
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            column: {
                                "query": chean_text,
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
    resp = es.search(index='chl', body=body)
    list = resp['hits']['hits']
    if list != []:
        for zd in list:
            title = zd['_source']['标题']
            # return "法器法律法规库有这条数据：" + title
            return True
    else:
        return False

def lar_esquc(title, column):
    if '转发' not in title:
        chean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)#.split('关于')[-1]
    else:chean_text=title
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            column: {
                                "query": chean_text,
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
    list = resp['hits']['hits']
    if list != []:
        for zd in list:
            title = zd['_source']['标题']
            # return "法器地方法规有这条数据：" + title
            return True
    else:
        return False

def save_sql_BidDocument(all_result,states=True):
    '''
    用于插入数据库
    :param k:
    :param all_result:
    :return:
    '''
    if states:
        connect = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
            'charset=gbk')
    else:
        connect = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=localhost;'
            'DATABASE=store;'
            'Trusted_Connection=yes;'
            'charset=gbk'
        )
    print('数据库连接成功')
    # 创建游标对象
    cursor = connect.cursor()
    # sql = "INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    # cursor.executemany(sql, all_result)
    cursor.execute(all_result)
    cursor.commit()
    print("链接插入success")
    cursor.close()
    connect.close()

shouludate = str(datetime.date.today()).replace('-', '.')+'LYJ'
def downfile(header,cookie,uuu, soup, content):
    '''
    下载文件
    :param soup:
    :param content:
    :return:
    '''
    href = re.compile('.*?\.(pdf|docx|doc|xlsx|xls|rar|zip|txt|wps)')
    tihuang = uuu.split('\\')[0].split('/')[0]
    folder_path = rf"C:\Users\小可爱\Desktop\python\青海省-数据收录\uploadfile\\"
    # 使用os.makedirs()创建文件夹，包括所有不存在的父文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    try:
        for test in soup.find_all('a', href=href):  # 找到所有的a标签然后用利用正则过滤
            ysrc = test.get('href')
            name = str(ysrc).split('=')[-1].split('/')[-1].split('\\')[-1]
            if type(ysrc) is str:
                try:
                    if 'http' in str(ysrc):
                        url = ysrc
                    else:
                        url = tihuang + ysrc.replace('../', '/').replace('./', '/')
                    response = requests.get(url, headers=header,cookies=cookie, stream=True)
                    # print(response.status_code)
                    if response.status_code == 200:
                        with open(rf'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}', 'wb') as file:
                            for chunk in response.iter_content(chunk_size=128):
                                file.write(chunk)
                        print(f"文件已下载到：'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}")
                        content = content.replace(ysrc,rf'/datafolder/新收录/{shouludate.replace(".", "")[:6]}/{name}')
                    else:
                        before = uuu.split('/')[-1].split('\\')[-1]
                        hao_before = uuu.replace(before, '')
                        if 'http' in str(ysrc):
                            url = ysrc
                        else:
                            url = hao_before + ysrc.replace('../', '/').replace('./', '/')
                        response = requests.get(url, headers=header, cookies=cookie,stream=True)
                        # print(response.status_code)
                        if response.status_code == 200:
                            with open(rf'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}', 'wb') as file:
                                for chunk in response.iter_content(chunk_size=128):
                                    file.write(chunk)
                            print(f"文件已下载到：'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}")
                            content = content.replace(ysrc,
                                                      rf'/datafolder/新收录/{shouludate.replace(".", "")[:6]}/{name}')
                        else:
                            print("下载文件时发生错误")
                except:
                    before = uuu.split('/')[-1].split('\\')[-1]
                    hao_before = uuu.replace(before, '')
                    if 'http' in str(ysrc):
                        url = ysrc
                    else:
                        url = hao_before + ysrc.replace('../', '/').replace('./', '/')
                    response = requests.get(url, headers=header, cookies=cookie,stream=True)
                    # print(response.status_code)
                    if response.status_code == 200:
                        with open(rf'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}', 'wb') as file:
                            for chunk in response.iter_content(chunk_size=128):
                                file.write(chunk)
                        print(f"文件已下载到：'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}")
                        content = content.replace(ysrc,
                                                  rf'/datafolder/新收录/{shouludate.replace(".", "")[:6]}/{name}')
                    else:
                        print("下载文件时发生错误")
    except:
        pass
    return content

def downfile_img(header,cookie,uuu, soup, content):
    '''
    下载文件
    :param soup:
    :param content:
    :return:
    '''
    tihuang = uuu.split('\\')[0].split('/')[0]
    folder_path = rf"C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\"
    # 使用os.makedirs()创建文件夹，包括所有不存在的父文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    try:
        for test in soup.find_all('img'):  # 找到所有的a标签然后用利用正则过滤
            ysrc = test.get('src')
            hhh = re.findall('.*?\.(jpeg|jpg|jpe|jif|jfi|jfif|jpx|jpm|mj2|png|gif|bmp|tiff|tif|raw|cr2|nef|orf|sr2|webp|psd|ai|svg|heif|heic)',ysrc)
            if hhh:
                name = str(ysrc).split('=')[-1].split('/')[-1].split('\\')[-1]
                if type(ysrc) is str:
                    try:
                        if 'http' in str(ysrc):
                            url = ysrc
                        else:
                            url = tihuang + ysrc.replace('../', '/').replace('./', '/')
                        response = requests.get(url, headers=header, cookies=cookie,stream=True)
                        # print(response.status_code)
                        if response.status_code == 200:
                            with open(rf'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}', 'wb') as file:
                                for chunk in response.iter_content(chunk_size=128):
                                    file.write(chunk)
                            print(f"文件已下载到：'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}")
                            content = content.replace(ysrc,
                                                      rf'/datafolder/新收录/{shouludate.replace(".", "")[:6]}/{name}')
                        else:
                            before = uuu.split('/')[-1].split('\\')[-1]
                            hao_before = uuu.replace(before, '')
                            if 'http' in str(ysrc):
                                url = ysrc
                            else:
                                url = hao_before + ysrc.replace('../', '/').replace('./', '/')
                            response = requests.get(url, headers=header, cookies=cookie,stream=True)
                            # print(response.status_code)
                            if response.status_code == 200:
                                with open(rf'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}', 'wb') as file:
                                    for chunk in response.iter_content(chunk_size=128):
                                        file.write(chunk)
                                print(f"文件已下载到：'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}")
                                content = content.replace(ysrc,
                                                          rf'/datafolder/新收录/{shouludate.replace(".", "")[:6]}/{name}')
                            else:
                                print("下载文件时发生错误")
                    except:
                        before = uuu.split('/')[-1].split('\\')[-1]
                        hao_before = uuu.replace(before, '')
                        if 'http' in str(ysrc):
                            url = ysrc
                        else:
                            url = hao_before + ysrc.replace('../', '/').replace('./', '/')
                        response = requests.get(url, headers=header, cookies=cookie,stream=True)
                        # print(response.status_code)
                        if response.status_code == 200:
                            with open(rf'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}', 'wb') as file:
                                for chunk in response.iter_content(chunk_size=128):
                                    file.write(chunk)
                            print(f"文件已下载到：'C:\\Users\\小可爱\\Desktop\\python\\青海省-数据收录\\uploadfile\\{name}")
                            content = content.replace(ysrc,
                                                      rf'/datafolder/新收录/{shouludate.replace(".", "")[:6]}/{name}')
                        else:
                            print("下载文件时发生错误")
    except:
        pass
    return content

def zhongwen(weizhi, txt):
    chinese_num_dict = {
        "一": "1", "二": "2", "三": "3", "四": "4", "五": "5", "六": "6", "七": "7",
        "八": "8",
        "九": "9", "十": weizhi, '○': "0",
        "〇": "0", "零": "0"}
    for key, value in chinese_num_dict.items():
        txt = txt.replace(key, value)
    return txt

def luokuanchuli(data_all,Description):
    try:
        tttt = re.findall(
            '(<p>\d{4}年\d{1,2}月\d{1,2}日)</p>',Description)
        for ttzz in tttt:
            qqqq=ttzz.replace('<p>','<p align="right">')
            Description = Description.replace(ttzz, qqqq)
    except:
        try:
            tttt = re.findall('(<p style="text-align:center;">\d{4}年\d{1,2}月\d{1,2}日)</p>', Description)
            for ttzz in tttt:
                qqqq = ttzz.replace('<p style="text-align:center;">', '<p align="right">')
                Description = Description.replace(ttzz, qqqq)
            tttt1 = re.findall('(<p align="center">\d{4}年\d{1,2}月\d{1,2}日)</p>', Description)
            for ttzz1 in tttt1:
                qqqq1 = ttzz1.replace('<p align="center">', '<p align="right">')
                Description = Description.replace(ttzz1, qqqq1)
        except:
            Description = Description
    for ii in list(data_all['value']):
        try:
            Description=Description.replace(rf'<br/>{str(ii)}<',rf'{str(ii)}<').replace(rf'<br>{str(ii)}<', rf'{str(ii)}<')
            Description = Description.replace(rf'<p>{str(ii)}</p>',rf'<p align="right">{str(ii)}</p>')
            dddd=re.findall(rf'<p style="text-align:center">{str(ii)}</p><p align="right">\d{4}年\d{1,2}月\d{1,2}日</p>',Description)
            for dz in dddd:
                pqqssss=dz.replace('<p style="text-align:center">','<p align="right">')
                Description = Description.replace(dz, pqqssss)
            dddd1 = re.findall(rf'<p style="text-align:center">{str(ii)}</p><p align="right">\d{4}年\d{1, 2}月\d{1, 2}日</p>',Description)
            for dz1 in dddd1:
                pqqssss1 = dz1.replace('<p align="center">', '<p align="right">')
                Description = Description.replace(dz1, pqqssss1)
        except:
            Description=Description
    return Description

def chuli(Description,dateall):
    for da in dateall:
        ppda = da[0]
        i = -1
        for dada in da:
            i += 1
            if i == 0:
                pass
            else:
                if i == 1:
                    if len(dada) == 3:
                        txt = zhongwen('', dada)
                        ppda = ppda.replace(f'年{da}月', f'年{txt}月')
                    elif len(dada) == 2:
                        if dada[0] == '十':
                            txt = zhongwen('1', dada)
                            ppda = ppda.replace(f'年{dada}月', f'年{txt}月')
                        else:
                            txt = zhongwen('0', dada)
                            ppda = ppda.replace(f'年{dada}月', f'年{txt}月')
                    else:
                        txt = zhongwen('10', dada)
                        ppda = ppda.replace(f'年{dada}月', f'年{txt}月')

                else:
                    if len(dada) == 3:
                        txt = zhongwen('', dada)
                        ppda = ppda.replace(f'月{dada}日', f'月{txt}日')
                    elif len(dada) == 2:
                        if dada[0] == '十':
                            txt = zhongwen('1', dada)
                            ppda = ppda.replace(f'月{dada}日', f'月{txt}日')
                        else:
                            txt = zhongwen('0', dada)
                            ppda = ppda.replace(f'月{dada}日', f'月{txt}日')
                    else:
                        txt = zhongwen('10', dada)
                        ppda = ppda.replace(f'月{dada}日', f'月{txt}日')
        txt = zhongwen('', ppda)
        ppda = ppda.replace(f'{ppda}', f'{txt}')
        Description = Description.replace(da[0], ppda)
    return Description

def save_sql_BidDocument_jiedu(all_result):
    '''
    用于插入数据库
    :param k:
    :param all_result:
    :return:
    '''
    # connect = pyodbc.connect(
    #     'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=ourdata;UID=saa;PWD=1+2-3..*Qwe!@#;'
    #     'charset=gbk')
    connect = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    print('数据库连接成功')
    # 创建游标对象
    cursor = connect.cursor()
    # sql = "INSERT INTO [ourdata].[dbo].[lfbjour] ([唯一标志],[标题],[全文],[发布部门],[类别],[发布日期],[收录日期]) VALUES (?,?,?,?,?,?,?)"  # ourdata.dbo.lfbjour
    sql = "INSERT INTO [自收录数据].[dbo].[lfbj-政策解读_copy1] ([唯一标志],[标题],[全文],[发布部门],[类别],[发布日期],[收录日期]) VALUES (?,?,?,?,?,?,?)"  # ourdata.dbo.lfbjour
    cursor.executemany(sql, all_result)
    cursor.commit()
    print("链接插入success")
    cursor.close()
    connect.close()

def lfbj_chong(title, column):
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            column: {
                                "query": title,
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
    resp = es.search(index='lfbj', body=body)
    list = resp['hits']['hits']
    if list != []:
        return True
        # for zd in list:
        #     title = zd['_source']['标题']
        #     # return "法器地方法规有这条数据：" + title
        #     return True
    else:
        return False
# from .QueryTitle import main_panduan
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    'Accept-Charset': 'utf-8'
}
def generate_unique_mark(title, release_date):
    combined = f"{title}{release_date}"
    md5_hash = hashlib.md5(combined.encode())
    return md5_hash.hexdigest()

def remove_unicode_chars(s):
    # 匹配Unicode控制字符和其他不可见字符
    # \u0000-\u001F 匹配ASCII控制字符
    # \u007F-\u009F 匹配ASCII控制字符和一些额外的控制字符
    # \u2000-\u206F 匹配一般空格字符
    # \u2028-\u2029 匹配行分隔符和段落分隔符
    # \uFEFF 匹配字节顺序标记
    # \uFFF0-\uFFFF 匹配其他特殊用途的字符
    pattern = r'[\u0000-\u001F\u007F-\u009F\u2000-\u206F\u2028-\u2029\uFEFF\uFFF0-\uFFFF]'
    return re.sub(pattern, '', s)

def check_date_format(text):
    pattern = r'\d{4}年\d{1,2}月\d{1,2}日'
    if re.search(pattern, text):
        return True
    return False

def remove_nbsp(soup,states=True):
    # 遍历所有的文本节点
    for tag in soup.find_all(True):
        if tag.string and isinstance(tag.string, NavigableString):
            # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
            # 将非换行空格替换为空格
            new_string = tag.string.replace(' ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(' ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace('  ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(" ", "")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace("  ", "")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(" ", "")
            tag.string.replace_with(new_string)
    a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
    soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
    # 遍历所有的<span>标签
    for span in soup.find_all('span'):
        # 如果span标签的文本为空，则移除它
        if not span.get_text().strip():
            span.decompose()
    for p in soup.find_all('p'):
        # 如果标签的文本为空，则移除它
        if not p.get_text().strip():
            p.decompose()
    if states:
        # 删除所有的<img>标签
        for img in soup.find_all('img'):
            img.decompose()
    for st in soup.find_all('script'):
        st.decompose()
    # 删除抄送
    for it in soup.find_all('p'):
        tag_text = it.get_text()
        if "抄送" in tag_text or '扫一扫' in tag_text:
            it.decompose()
    # 将 soup 转换为字符串
    html_str = str(soup)
    # 使用正则表达式移除 HTML 注释
    html_str_without_comments = re.sub(r'<!--(.*?)-->', '', html_str, flags=re.DOTALL)
    # 如果需要，可以重新解析成一个新的 soup 对象
    soup = BeautifulSoup(html_str_without_comments, 'html.parser')
    # # 为最终落款格式未靠右的文章添加靠右
    # soup = self.add_right(soup, ['局', '会'])
    # soup = self.add_right(soup, ['年', '月', '日'])
    return soup

def format_date(date_str):
    # 分割日期字符串
    year, month, day = date_str.split('.')

    # 确保月份和日期前面如果有数字小于 10，则前面加上一个零
    formatted_month = f"{int(month):02d}"
    formatted_day = f"{int(day):02d}"

    # 返回格式化的日期字符串
    return f"{year}.{formatted_month}.{formatted_day}"

def determine(style):
    not_in_lt = ['font-family', 'margin-top', 'margin-bottom', 'font-size', 'line-height']
    for it in not_in_lt:
        if it in style:
            return True
    return False

def soup_cal(soup_ture):
    """
    传入正文部分soup，传出初步清洗的结果soup
    :param soup_ture:
    :return:
    """
    # 保留列表
    not_lt = ["text-align:right", "text-align:center", "text-align: right"]
    # 移除所有style属性，但保留居中，靠右，加粗
    for tag in soup_ture.find_all(True):
        # text_1 = tag.get_text()
        style = tag.get('style')
        data_index = tag.get('data-index')
        if data_index:
            del tag['data-index']
        if style:
            if determine(style):
                if 'text-align' in style:
                    # 获取当前元素的style属性值
                    style_value = tag['style']
                    # 将style值分割成多个样式
                    styles = style_value.split(';')
                    new_styles = []
                    for it in styles:
                        if it.strip() in not_lt:
                            new_styles.append(it.strip())
                    # 重新组合样式
                    if new_styles:
                        tag['style'] = '; '.join(new_styles)
                    else:
                        del tag['style']
                        continue
                else:
                    del tag['style']
                    continue
            else:
                if 'text-align' in style:
                    # 获取当前元素的style属性值
                    style_value = tag['style']
                    # 将style值分割成多个样式
                    styles = style_value.split(';')
                    if "text-align:left" in styles:
                        del tag['style']
                        continue
                else:
                    del tag['style']
                    continue
    return soup_ture

import re
from elasticsearch import Elasticsearch
from botpy import logging
_log = logging.get_logger()
"""
本方法用于，拿到了标题先判断系统里有没有，没有的话，才进行全文以及其他字段收录
"""
# es = Elasticsearch(['http://10.0.0.1:8041'], basic_auth=('elastic', 'Cdxb1998123!@#'))
es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)
ddd = '重庆'
def select(list_name, titl, chean_text, quer, fm):
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


def check_existence(input_data, title, column, quer, fm):
    '''
    该函数用于判断新收录文件标题是否存在法器当中
    :param input_data: 新收录文件标题
    '''
    title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
    if '转发' not in title:
        chean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  #.split('关于')[-1]
    else:
        chean_text = title
    a = select(column, title, chean_text, quer, fm)
    if a:
        # print(rf'{input_data}存在于法器中')
        return True
    else:
        # print(rf'{input_data}不存在于法器中')
        return False


def lar_esquc(title, column):
    if '转发' not in title:
        clean_text = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  #.split('关于')[-1]
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
    if list_a != []:
        for zd in list_a:
            title = zd['_source']['标题']
            _log.info(f"法器地方法规有这条数据： {title}")
            return True
    else:
        return False


def query(list_name, ddd1, ddd2):
    query1 = {
        "query": {"bool": {
            "must": [{"match_phrase": {list_name: ddd1}},
                     {"match_phrase": {list_name: ddd2}}]}}}
    query2 = {"query": {"match": {list_name: ddd2}}}
    return [query1, query2]


def main_panduan(title_a, issued_number):
    chatitle = title_a
    query1 = query('标题', ddd, chatitle)[0]
    query2 = query('发文字号', ddd, issued_number)[1]
    a = check_existence(title_a, title_a, '标题', query1, '831')
    b = check_existence(issued_number, issued_number, '发文字号', query2, '831')
    if (lar_esquc(title_a, '标题') or a) and title_a[-3:] != '...':
        return True
    else:
        if (lar_esquc(issued_number, '发文字号') or b) and len(issued_number.strip()) > 2:
            return True
    return False
def tupiangeshi(self,Description):
    '''设置图片格式'''
    ddd = re.findall('<img.*?>', Description)
    for dzz in ddd:
        ppp = re.findall('src="/datafolder.*?"', dzz)
        try:
            pppqqq = '<img style="max-width: 100%; display:block; margin:0 auto;" ' + ppp[0] + '/>'
            Description = Description.replace(dzz, pppqqq)
        except:
            Description=Description
    return Description

def annex_get(url, save_path, headers, save_path_real):
    """
    本函数用于附件内容获取
    :param url: 附件的URL
    :param save_path: 保存文件名
    :param headers: 请求头
    :param save_path_real: 完整的保存路径
    :return: 下载是否成功 (True/False)
    """
    # 构造完整路径
    base_directory = os.path.join('E:/下载附件/', save_path_real)
    save_path_real = os.path.join(base_directory, save_path)

    # 检查文件是否已存在
    if os.path.exists(save_path_real):
        _log.info(f"{save_path} 附件文件已经存在！！！")
        return True

    # 确保父目录存在
    os.makedirs(base_directory, exist_ok=True)

    # 检查并设置目录权限
    try:
        os.chmod(base_directory, 0o777)  # 设置目录权限为可读写执行
    except Exception as e:
        _log.error(f"设置目录权限时发生错误: {e}")

    # 休眠一段时间
    sleep = random.uniform(0, 2)
    _log.info(f"休眠{sleep}秒,目前获取地址为:{url}")
    time.sleep(sleep)

    # 发起请求
    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            with open(save_path_real, "wb") as ac:
                ac.write(response.content)
            _log.info(f"下载成功!")
            return True
        elif response.status_code == 521:
            _log.error(f"错误: 521!")
            return False
        elif response.status_code == 404:
            _log.error(f"错误: 下载失败，网页打不开！！！")
            _log.error(f"错误: {url}")
            return False
    except Exception as e:
        _log.error(f"发生错误: {e}")
        return False



def set_right_alignment(html_content):
    """
    本函数用于检查 HTML 中的标签，如果标签内的文本长度不超过 20 个字符，
    并且包含关键字之一，并且不包含排除字符串之一，则将这些标签的样式设置为靠右对齐。

    :param html_content: HTML 内容字符串
    :return: 修改后的 HTML 内容字符串
    """
    # 关键字列表
    keywords = ['海关', '局', '会', '年', '月', '日']

    # 排除字符串列表
    exclude_strings = ['条', '章','解释','指引','服务']

    # 遍历所有标签
    for tag in html_content.find_all('p'):
        # 获取标签的文本内容
        text = tag.get_text(strip=True)

        # 检查文本长度是否不超过 20 个字符
        if len(text) <= 20:
            # 检查文本是否包含关键字之一
            if any(keyword in text for keyword in keywords):
                # 检查文本是否包含排除字符串之一
                if not any(exclude_string in text for exclude_string in exclude_strings):
                    # 设置样式为靠右对齐
                    tag['style'] = 'text-align: right;'

    # 返回修改后的 HTML 内容
    return html_content

def format_date(date_str):
    # 分割日期字符串
    year, month, day = date_str.split('.')

    # 确保月份和日期前面如果有数字小于 10，则前面加上一个零
    formatted_month = f"{int(month):02d}"
    formatted_day = f"{int(day):02d}"

    # 返回格式化的日期字符串
    return f"{year}.{formatted_month}.{formatted_day}"
def main1():
    not_Send_word_numbers=[]
    for i in range(6):
        url = f"https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/index_{i}.html"
        if i == 0:
            url = "https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/index.html"
        response = requests.get(url, headers=headers, verify=False)
        MyHtml = response.text.encode('iso-8859-1').decode('utf-8')
        res = etree.HTML(MyHtml)
        zcwjk = res.xpath('//ul[@class="tab-item"]/li[@class="clearfix"]')
        for zcw in zcwjk:
            try:
                # 'http://www.cqws.gov.cn/xzfbm_73744/sfj_1/zwgk_72016/sf/kjgh1458_383320/jytabl230301/202309/t20230911_12323524.html'
                # '../../../../../xzfbm_73744/sfj_1/zwgk_72016/sf/kjgh1458_383320/jytabl230301/202309/t20230911_12323524.html'
                href = 'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj'+''.join(zcw.xpath("./a/@href")).strip()[1:]
                # href ='https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/202101/t20210126_8820148.html'
                fujian = ''.join(zcw.xpath("./a/@href"))[2:].split('/')[0].strip()
                if 'scjgj.cq.gov.cn' in ''.join(zcw.xpath("./a/@href")).strip():
                    href = 'https:'+''.join(zcw.xpath("./a/@href")).strip()
                    fujian = ''.join(zcw.xpath("./a/@href")).replace('//scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/','').split('/')[0].strip()
                # fujian = '202101'
                title = ''.join(zcw.xpath('./a/@title')).strip()  # 标题
                Release_date = ''.join(zcw.xpath('./span/text()')).replace('年', '.').replace('月', '.').replace('日', '').strip().replace('-', '.').replace('-', '.')
                time.sleep(3)
                for t in range(3):
                    try:
                        response1 = requests.get(href, headers=headers, verify=False)
                        if response1.status_code == 200:
                            break
                    except:
                        print(f'重试{t}')
                if response1.status_code == 404:
                    print('404', href, url, title)
                Html =response1.text.encode('iso-8859-1').decode('utf-8')
                res1 = etree.HTML(Html)
                tr_text = res1.xpath('//table[@class="zwxl-table"]/tbody/tr')
                dict1={}
                for tr in tr_text:
                    for t1,t2 in zip(tr.xpath('./td[@class="t1"]/text()'),tr.xpath('./td[@class="t2"]/text()')):
                       dict1[t1.strip()] = t2
                Send_word_numbers=''
                for di in list(dict1.keys()):
                    if '发文字号'in di:
                        Send_word_numbers=dict1[di]
                if not Send_word_numbers:
                    not_Send_word_numbers.append([title,Release_date,href,url])
                if main_panduan(title, Send_word_numbers):
                    print(title +'-'+Send_word_numbers+'='+'es数据库已有'+'第'+str(i)+'页')
                else:
                    print(title +'='+ 'es数据库没有'+href+'-'+url+'第'+str(i)+'页')
                    # 使用BeautifulSoup解析HTML
                    soup = BeautifulSoup(Html, 'html.parser')
                    # 找到class为a24Detail的div元素
                    div_a24Detail1 = soup.find('div', class_=['trs_editor_view TRS_UEDITOR trs_paper_default trs_word','trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web','view TRS_UEDITOR trs_paper_default trs_word trs_web','view TRS_UEDITOR trs_paper_default trs_word','trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web trs_excel','trs_editor_view TRS_UEDITOR trs_paper_default trs_web','view TRS_UEDITOR trs_paper_default','trs_editor_view TRS_UEDITOR trs_paper_default trs_external','view TRS_UEDITOR trs_paper_default trs_external'])

                    if div_a24Detail1==None:
                        text_href = soup.find('p',style="font-size: 14px;line-height: 30px;margin-bottom: 30px;")
                        if not text_href:
                            text_href = soup.find('p', style="TEXT-ALIGN: center")
                        if not text_href:
                            text_href = soup.find('div',class_="zwxl-article")
                        # 定义文件扩展名列表
                        file_extensions = ['.xlsx', '.docx', '.pdf','.doc']
                        # 查找包含指定文件扩展名的 <a> 标签
                        links = []
                        href_title=[]
                        for ext in file_extensions:
                            for link in text_href.find_all('a'):
                                if ext in link['href']:
                                    links.append(
                                        'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/' + fujian + link['href'][1:])

                                    link[
                                        'href'] = '/datafolder/新收录/202409/' + 'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/' + fujian + \
                                                  link['href'][1:]
                                if ext not in link.text.strip():
                                    href_title.append(link.text.strip() + ext)
                                else:
                                    href_title.append(link.text.strip())
                        for lin,ht in zip(links,href_title):
                            annex_get(lin,headers=headers,save_path=ht,save_path_real='重庆市发改委其他文件')
                        div_a24Detail1 = remove_nbsp(text_href.parent)
                    elif len(div_a24Detail1.text)<100:
                        # 定义文件扩展名列表
                        file_extensions = ['.xlsx', '.docx', '.pdf','.doc']
                        # 查找包含指定文件扩展名的 <a> 标签
                        links = []
                        href_title = []
                        for ext in file_extensions:
                            for link in div_a24Detail1.find_all('a'):
                                if ext in link['href']:
                                    links.append(
                                        'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/' + fujian + link['href'][1:])

                                    link[
                                        'href'] = '/datafolder/新收录/202409/' + 'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/' + fujian + \
                                                  link['href'][1:]
                                    if ext not in link.text.strip():
                                        href_title.append(link.text.strip() + ext)
                                    else:
                                        href_title.append(link.text.strip())
                        for lin,ht in zip(links,href_title):
                            annex_get(lin,headers=headers,save_path=ht,save_path_real='重庆市发改委其他文件')
                        div11 = None
                        div_a24Detail1=remove_nbsp(div_a24Detail1)

                    else:
                        div_a24Detail1 = set_right_alignment(div_a24Detail1)
                        div_a24Detail = soup_cal(div_a24Detail1)
                        # # 删除id为'a1'的`<div>`元素
                        # div_a24Detail.find(id='a1').decompose()
                        Release_time=''
                        for p in div_a24Detail.find_all('p'):
                            # 在“联系人：”和“联系电话：”之间插入空格
                            text = p.get_text()
                            if '联系电话：' in text and '联系人：' in text:
                                p['style'] = 'white-space: pre;'
                                new_text = text.replace('联系人：', '联系人：                  ')  # 插入6个空格
                                if p.string is not None:
                                    p.string.replace_with(new_text)
                            if '20' in text and '年' in text and '月' in text and '日' in text and check_date_format(text):
                                Release_time = text.replace('年', '.').replace('月', '.').replace('日', '').strip().replace('-', '.').replace('-', '.')
                        if Release_time:
                            Release_date=Release_time
                        div_a24Detail = remove_nbsp(div_a24Detail)
                        # 查找包含指定文件扩展名的 <a> 标签
                        # 定义文件扩展名列表
                        file_extensions = ['.xlsx', '.docx', '.pdf', '.doc']
                        links = []
                        href_title = []
                        for ext in file_extensions:
                            for link in div_a24Detail.find_all('a'):
                                if ext in link['href'] and title not in link.text.strip():
                                    links.append(
                                        'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/' + fujian + link['href'][1:])

                                    link['href']='/datafolder/新收录/202409/' + 'https://scjgj.cq.gov.cn/zfxxgk_225/zcwj/qtwj/' + fujian + link['href'][1:]
                                    if ext not in link.text.strip():
                                        href_title.append(link.text.strip() + ext)
                                    else:
                                        href_title.append(link.text.strip())
                        for lin, ht in zip(links, href_title):
                            annex_get(lin, headers=headers, save_path=ht, save_path_real='重庆市发改委其他文件')
                        div11 = str(div_a24Detail)
                        div_a24Detail1=div_a24Detail
                    Release_date = format_date(Release_date)
                    md5_value = generate_unique_mark(title, Release_date)  # 标签

                    bumen = {
                        '重庆市市场监督管理局': catagroy_select(title,div_a24Detail1.text)
                    }
                    xiaoli = {
                        '地方工作文件': 'XP10'
                    }
                    shixiao = '01'
                    leibie = 类别判断.get_catagroy(title)
                    soup_text=div_a24Detail1

                    sql = rf"INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES ('{md5_value}','{title}','{soup_text}','{bumen['重庆市市场监督管理局']}','{leibie}','{Release_date}','{xiaoli['地方工作文件']}','{Release_date}','{Send_word_numbers}','{shixiao}','{href}','{shouludate}')"
                    save_sql_BidDocument(sql)
            except Exception as e:
                print('报错',e,title,url)
if __name__ == '__main__':
    main1()