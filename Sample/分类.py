# -*- coding: utf-8 -*-
import re
import jieba
import pyodbc
import logging
import requests
import warnings
from datetime import datetime
from functools import lru_cache
from collections import Counter
from pyquery.pyquery import PyQuery as pq
from concurrent.futures import ThreadPoolExecutor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

warnings.filterwarnings('ignore')
logging.getLogger('jieba').setLevel(logging.WARNING)
headers = {'Referer': 'https://lawdoo.com/',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76'}

session = requests.Session()
session.headers.update(headers)


# # 连接到数据库
# connect = pyodbc.connect(
#         'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
#         'charset=gbk')
# print('数据库连接成功')
# # 创建游标对象
# cursor = connect.cursor()
# sql="SELECT 法规标题,全文 FROM [自收录数据].[dbo].[cswgsj_fql] WHERE [收录时间] LIKE N'%2024.07.%' and [ID]>8059"
# cursor.execute(sql)
# data=cursor.fetchall()
# # print(data)
# cursor.close()
# connect.close()
@lru_cache(maxsize=128)
def get_data_from_api(*args):
    # 将参数从元组形式转换回字典形式
    params = dict(args)
    response = session.get('https://api.lawdoo.com/api/FD/GetLeftMenuList', params=params)
    return response.json()


stopwords_path = r"D:\pystore\Gitstore\公司1\呆萌的停用词表.txt"
stopwords = [line.strip() for line in open(stopwords_path, 'r', encoding='utf-8').readlines()]

def keyjieba(text):
    rule = re.compile(u"[^\u4E00-\u9FA5]")
    # 去除标点符号
    clean_text = rule.sub(' ', text)
    # 去除停用词并进行分词
    # tokenized_text = [w for w in list(jieba.cut(clean_text, cut_all=False)) if w not in stopwords]
    tokenized_text = [w for w in list(jieba.lcut(clean_text)) if w not in stopwords]
    return " ".join(tokenized_text)


def extract_keywords(text):
    # 将文本转换为词频矩阵
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(text)
    # 计算TF-IDF
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    # 获取词袋模型中的所有词语
    words = vectorizer.get_feature_names_out()
    # 获取关键词
    weights = tfidf.toarray()[0]
    keyword_indices = weights.argsort()[-30:][::-1]  # 获取排名前n_keywords的关键词索引
    keywords = [words[idx] for idx in keyword_indices]
    keyword_indices1 = weights.argsort()[-80:][::-1]  # 获取排名前n_keywords的关键词索引
    keywords1 = [words[idx] for idx in keyword_indices1]
    return keywords, keywords1


def key_word(Description, titl):
    # 调用关键词提取函数
    # 分割文本为句子
    description = pq(Description).text()
    text_sentences = re.split(r'[。！？]', description)
    text_sentences = [sentence.strip() for sentence in text_sentences if sentence.strip() != '']
    # 分词和关键词提取
    with ThreadPoolExecutor() as executor:
        cut_texts = list(executor.map(keyjieba, text_sentences))
    if '关于修订' in titl:
        cut_texts.append('修订')
    extractkeywords = extract_keywords(cut_texts)
    keywords = extractkeywords[0]
    name = titl[:3].strip()
    titlewei = titl.split('印发')[-1].split('关于')[-1].split('转发')[-1]
    wei = titlewei.split('的')[-1]
    title = titlewei.replace('的' + wei, '')
    title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
    keyword = []
    keyword_counter = Counter(keywords)
    kerd = {key: keyword_counter[key] for key in keyword_counter if
            key in title and '政府' not in key and name not in key}
    if len(kerd) < 3:
        keywords = extractkeywords[-1]
        keyword_counter = Counter(keywords)
        kerd = {key: keyword_counter[key] for key in keyword_counter if
                key in title and '政府' not in key and name not in key}

    sorted_keywords = sorted(kerd, key=kerd.get, reverse=False)
    return sorted_keywords


def catagroy_select(description, titl):
    try:
        word = key_word(description, titl)
        lll = word
        kee = " ".join(word)
        timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
        params = {'lib': 'lar', 'menuConditions': '0,0,0,0', 'conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;0',
                  'a': f'{timestamp}', 'isPrecision': 'true', '_': f'{timestamp}'}
        params_tuple = tuple(params.items())
        data_list1 = get_data_from_api(*params_tuple)
        while len(data_list1) < 2 and ' ' in kee:
            lll = lll[1:-1]
            kee = " ".join(lll)
            timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
            params1 = {'lib': 'lar', 'menuConditions': '0,0,0,0', 'conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;0',
                       'a': f'{timestamp}', 'isPrecision': 'true', '_': f'{timestamp}'}
            # 将字典参数转换为元组
            params_tuple1 = tuple(params1.items())
            data_list1 = get_data_from_api(*params_tuple1)
        data_list = data_list1['z_menuList'][1]
        max_dict = max(data_list, key=lambda x: x['sum'])
        one_id = max_dict["ID"]
        one_ids = ['106', '111', '112', '113', '114', '115', '116', '117', '119']
        if one_id in one_ids:
            max_dictdetail_two = max_dict
        else:

            timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
            paramdetail = {'lib': 'lar', 'menuConditions': f'0,{one_id},0,0',
                           'conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;{one_id}', 'a': f'{timestamp}',
                           'isPrecision': 'true', '_': f'{timestamp}'}
            params_tuple2 = tuple(paramdetail.items())
            data_list1detail = get_data_from_api(*params_tuple2)
            data_listdetail = data_list1detail['z_menuList'][1]
            max_dictdetail = max(data_listdetail, key=lambda x: x['sum'])
            two_id = max_dictdetail["ID"]
            two_ids = ['018', '032', '037', '038', '040', '044', '050']
            if two_id in two_ids:
                max_dictdetail_two = max_dictdetail
            else:
                timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
                paramdetail_two = {'lib': 'lar', 'menuConditions': f'0,{two_id},0,0',
                                   'conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;{two_id}', 'a': f'{timestamp}',
                                   'isPrecision': 'true', '_': f'{timestamp}'}
                params_tuple3 = tuple(paramdetail_two.items())
                data_list1detail_two = get_data_from_api(*params_tuple3)
                data_listdetail_two = data_list1detail_two['z_menuList'][1]
                if len(data_listdetail_two) == 0:
                    max_dictdetail_two = max_dictdetail
                else:
                    max_dictdetail_two = max(data_listdetail_two, key=lambda x: x['sum'])
        leibeidetail = str(max_dictdetail_two['Value']) + '/' + str(max_dictdetail_two['sum']) + '/' + str(
            max_dictdetail_two['ID']) + '/' + str(kee)
        category = max_dictdetail_two['ID']
        if len(category) > 5:
            leibeidet = category[:3] + ';' + category[:5] + ';' + category
        elif len(category) == 5:
            leibeidet = category[:3] + ';' + category
        else:
            leibeidet = category
    except:
        leibeidetail = ''
        leibeidet = ''
    print(leibeidet)
    return leibeidet


