# -*- coding: utf-8 -*-
import warnings
import time

import pandas
import pandas as pd
import requests
import cchardet
import random
import os
from unidecode import unidecode
from bs4 import BeautifulSoup,Comment
import traceback
from lxml import etree
import pyodbc
from functools import partial
import datetime
import re
import html
import unicodedata
from multiprocessing.dummy import Pool
from pyquery import PyQuery as pq
from elasticsearch6 import Elasticsearch
import warnings
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

def save_sql_BidDocument(all_result):
    '''
    用于插入数据库
    :param k:
    :param all_result:
    :return:
    '''
    connect = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
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

shouludate = str(datetime.date.today()).replace('-', '.')
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
    folder_path = rf"E:\下载附件\img"
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
                            with open(rf'E:\下载附件\img\{name}', 'wb') as file:
                                for chunk in response.iter_content(chunk_size=128):
                                    file.write(chunk)
                            print(f"文件已下载到：'E:\下载附件\img\{name}")
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
                                with open(rf'E:\下载附件\img\{name}', 'wb') as file:
                                    for chunk in response.iter_content(chunk_size=128):
                                        file.write(chunk)
                                print(f"文件已下载到：'E:\下载附件\img\{name}")
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
                            with open(rf'E:\下载附件\img\{name}', 'wb') as file:
                                for chunk in response.iter_content(chunk_size=128):
                                    file.write(chunk)
                            print(f"文件已下载到：'E:\下载附件\img\uploadfile\\{name}")
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