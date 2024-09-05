import os
import time
import random
from bs4 import BeautifulSoup, NavigableString
import hashlib
from sqlalchemy import create_engine
import logging
from query.QueryTitle import main_panduan
import re
import pyodbc
import requests
from datetime import datetime
from pyquery.pyquery import PyQuery as pq
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor

_log = logging.getLogger(__name__)


def annex_get(url, save_path, headers, save_path_real='重庆市其他文件'):
    """
    本函数用于附件内容获取
    :param url: 文件的URL
    :param save_path: 保存名
    :param headers: 请求头
    :param save_path_real: 保存的实际路径，默认为'重庆市其他文件'
    :return: True 表示下载成功，False 表示下载失败
    """
    # 构建完整的保存路径
    save_path_real = f'E:/JXdata/{save_path_real}/' + save_path

    # 检查并创建目录
    directory = os.path.dirname(save_path_real)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 检查文件是否已存在
    if os.path.exists(save_path_real):
        _log.info(f"{save_path} 附件文件已经存在！！！")
        return

    # 设置随机休眠时间
    sleep_time = random.uniform(0, 2)
    _log.info(f"休眠{sleep_time:.2f}秒, 目前获取地址为: {url}")
    time.sleep(sleep_time)

    # 发起请求
    req = requests.get(url, headers=headers, verify=False)

    try:
        if req.status_code == 200:
            with open(save_path_real, "wb") as ac:
                ac.write(req.content)
            _log.info(f"下载成功!")
            return True
        elif req.status_code == 521:
            _log.error(f"错误: 521!")
            return False
        elif req.status_code == 404:
            _log.error(f"错误: 下载失败，网页打不开！！！")
            _log.error(f"错误: {url}")
            return False
    except Exception as e:
        _log.error(f"发生错误: {e}")
        return False


def fetch_url(url, headers):
    """
    获取网页信息内容,soup
    cl_num:重试次数为3
    :param headers: 请求头
    :param url:获取页面url
    :return: soup
    """
    cl_num = 3
    for it in range(cl_num):
        try:
            sleep = random.uniform(0, 2)
            _log.info(f"休眠{sleep}秒")
            time.sleep(sleep)
            # 发送 HTTP GET 请求
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                # 返回页面内容
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
        except pyodbc.OperationalError as e:
            _log.info(f"出错！      {e}")
            sleep = random.uniform(2, 4)
            _log.info(f"休眠{sleep}秒")
            time.sleep(sleep)
            _log.info("==========================")
            if it == cl_num - 1:
                _log.info("该网站内容无法获取")
                _log.info(f"网站url:  {url}")
    return soup


def to_mysql(df, table_name):
    """
    将数据写入本地库
    :param df: 数据df
    :param table_name: 表名
    :return:
    """
    # 数据库连接信息
    server = 'localhost'
    database = 'test'
    # Integrated Security=True启用Windows身份验证
    connection_string = f'mssql+pyodbc://{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
    # 创建连接
    try:
        engine = create_engine(connection_string)
    except pyodbc.OperationalError as e:
        _log.info(f"Connection error: {e}")
        exit()
    df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
    # 关闭连接
    engine.dispose()


def get_md5(string):
    """
    计算md5值
    :param string:
    :return:
    """
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


def soup_cal(soup_ture):
    """
    传入正文部分soup，传出初步清洗的结果soup
    :param soup_ture:
    :return:
    """
    not_dt = {"text-align:right", "text-align:center", "text-align: right", 'text-align: center', 'id'}

    def process_style(tag_s):
        style = tag_s.get('style')
        if style:
            styles = [s.strip() for s in style.split(';') if s.strip()]
            new_styles = [s for s in styles if s in not_dt]
            for s in styles:
                # 如果样式是 text-align:end 或 text-align: end，则替换为 text-align:right
                if s.startswith('text-align:end') or s == 'text-align: end':
                    s = 'text-align:right'
                if s in not_dt or s.startswith('text-align:right'):
                    new_styles.append(s)

            if new_styles:
                tag_s['style'] = '; '.join(new_styles)
            else:
                del tag_s['style']

    for tag in soup_ture.find_all(True):
        attrs_to_remove = ['data-index', 'id', 'class', 'align', 'type']

        for attr in attrs_to_remove:
            # tag.attrs 是一个字典，包含了标签的所有属性
            if attr in tag.attrs:
                del tag[attr]
        process_style(tag)
    # 处理可能的顶级元素样式
    process_style(soup_ture)
    return soup_ture


def convert_chinese_date_to_numeric(date_str):
    """
    定义汉字数字到阿拉伯数字的映射
    :param date_str: 需要检测的发布日期字符串
    :return:
    """
    # 汉字数字集合
    chinese_numbers = set('〇零一二两三四五六七八九十年月日')
    # 检查字符串中是否包含汉字数字
    if not any(char in chinese_numbers for char in date_str):
        return date_str
    chinese_num_map = {
        '零': '0', '〇': '0',
        '一': '1', '二': '2', '两': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
    }
    # 定义月份和日期的映射
    month_day_map = {
        '一': '01', '二': '02', '三': '03', '四': '04', '五': '05',
        '六': '06', '七': '07', '八': '08', '九': '09', '十': '10',
        '十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
        '十六': '16', '十七': '17', '十八': '18', '十九': '19', '二十': '20',
        '二十一': '21', '二十二': '22', '二十三': '23', '二十四': '24', '二十五': '25',
        '二十六': '26', '二十七': '27', '二十八': '28', '二十九': '29', '三十': '30',
        '三十一': '31'
    }

    parts = date_str.split('.')
    converted_parts = []
    # 转换年份
    year = parts[0]
    converted_year = ''
    for char in year:
        if char in chinese_num_map:
            converted_year += chinese_num_map[char]
    converted_parts.append(converted_year)
    # 转换月份
    month = parts[1]
    converted_month = month_day_map.get(month, '')
    converted_parts.append(converted_month)
    # 转换日期
    day = parts[2]
    converted_day = month_day_map.get(day, '')
    converted_parts.append(converted_day)

    # 重新组合日期
    return '.'.join(converted_parts)


def soup_get_date(soup):
    """
    运用于其他文件,在文件的表格中获取发布日期以及发文字号
    :param soup:
    :return:
    """
    data_dt = {
        "发文字号": None
    }
    in_lt = ["成文日期", "发布日期"]
    table_t = soup.find('table', class_="zwxl-table")
    tr_all = table_t.find_all('tr')
    for tag in tr_all:
        tag_text = tag.get_text()
        if any(key in tag_text for key in in_lt):
            tag_text = tag_text.strip()
            # 定义正则表达式模式，匹配包含“成文日期”的行
            pattern = r'\[ 成文日期 \]\s*(\d{4}-\d{2}-\d{2})'
            # 使用正则表达式搜索匹配项
            match = re.search(pattern, tag_text)
            if match:
                # 提取出日期字符串
                date_str = match.group(1)
                # 将日期格式化为 "YYYY.MM.DD" 格式
                formatted_date = date_str.replace('-', '.')
                data_dt["发布日期"] = formatted_date
        if "发文字号" in tag_text:
            # 定义正则表达式模式，匹配包含“发文字号”的行
            pattern = r'\[ 发文字号 \]\s*(.*)'
            match = re.search(pattern, tag_text)
            if match:
                code = match.group(1).strip()
                # 检查是否为空
                if code:
                    data_dt["发文字号"] = code
    return data_dt




def remove_nbsp(soup, is_add_right=True):
    """
    对初步清洗的soup进行进步格式清洗
    :param is_add_right: 是否为最后加上靠右
    :param soup: 初步清洗的soup
    :return: 最终结果
    """
    # 遍历所有的文本节点
    for tag in soup.find_all(True):
        if tag.string and isinstance(tag.string, NavigableString):
            # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
            # 将非换行空格替换为空格
            new_string = tag.string.replace(' ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(' ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace('  ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(" ", " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace("  ", " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(" ", " ")
            tag.string.replace_with(new_string)
    a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
    soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
    # 遍历所有的<span>标签
    for span in soup.find_all('span'):
        # 如果span标签的文本为空，则移除它
        if not span.get_text().strip():
            span.decompose()
    # for p in soup.find_all('p'):
    #     if not p.get_text().strip():
    #         p.decompose()
    # 删除所有的video标签
    for a in soup.find_all('video'):
        if not a.get_text().strip():
            a.decompose()
    # 删除所有的<img>标签
    for img in soup.find_all('img'):
        img.decompose()
    for st in soup.find_all('script'):
        st.decompose()
    # 如果有抄送，删除抄送
    for it in soup.find_all('p'):
        tag_text = it.get_text()
        if "抄送" in tag_text:
            it.decompose()
    # 将 soup 转换为字符串
    html_str = str(soup)
    # 使用正则表达式移除 HTML 注释
    html_str_without_comments = re.sub(r'<!--(.*?)-->', '', html_str, flags=re.DOTALL)
    # 重新解析成一个新的 soup 对象
    soup = BeautifulSoup(html_str_without_comments, 'html.parser')
    # if is_add_right:
    #     # 为最终落款格式未靠右的文章添加靠右
    #     soup = add_right(soup, ['局', '会'])
    #     soup = add_right(soup, ['年', '月', '日'])
    return soup


def set_right_alignment(html_content):
    """
    本函数用于检查 HTML 中的标签，如果标签内的文本长度不超过 20 个字符，
    并且包含关键字之一，并且不包含排除字符串之一，则将这些标签的样式设置为靠右对齐。

    :param html_content: HTML 内容soup
    :return: 修改后的 HTML 内容字符串
    """
    # 关键字列表
    keywords = ['海关', '局', '会', '年', '月', '日']
    # 排除字符串列表
    exclude_strings = ['条', '章', '解释', '指引', '服务']
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


def is_a_tag(html_tag):
    html_tag = str(html_tag)
    # 匹配<a>标签
    pattern = r'^<a[^>]*>.*</a>$'
    return bool(re.match(pattern, html_tag))


def add_right(soup, in_lt):
    # 给非靠右标签添加靠右属性
    # in_lt = ['局', '会']
    found = False  # 添加一个标志变量来记录是否找到了符合条件的标签
    for tag in reversed(soup.find_all(True)):
        if is_a_tag(tag):
            continue
        text_1 = tag.get_text()
        for it in in_lt:
            if it in text_1:
                style_1 = tag.get('style')
                if style_1 and 'right' not in style_1:
                    # 如果已有 style 属性且不包含 'right'，则修改 style 属性
                    tag['style'] = 'text-align: right;'
                    _log.info(f"添加style于 {tag.get_text()}")
                elif not style_1:
                    # 如果没有 style 属性，则添加
                    tag['style'] = 'text-align: right;'
                    _log.info(f"添加style于 {tag.get_text()}")
                found = True  # 设置标志变量为 True
                break  # 找到匹配后跳出内部循环
        if found:
            break  # 找到第一个匹配项后跳出外层循环
    return soup
