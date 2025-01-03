import configparser
import os
import time
import random
from bs4 import BeautifulSoup, NavigableString
import hashlib
from sqlalchemy import create_engine
import logging
from elasticsearch import Elasticsearch
from query.QueryTitle import main_panduan
from Sample.分类 import get_data_from_api, key_word
import re
import pyodbc
import requests
from datetime import datetime
from pyquery.pyquery import PyQuery as pq

_log = logging.getLogger(__name__)
# Elasticsearch 配置
es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


def load_config(env='development'):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config[env]


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


def catagroy_select(description, titl):
    """
    该方法用于获取文件的类别编号
    :param description: 全文信息
    :param titl: 法规标题
    :return: 法规编号
    """
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
        leibiename = str(max_dictdetail_two['Value'])
        leibeidetail = leibiename + '/' + str(max_dictdetail_two['sum']) + '/' + str(
            max_dictdetail_two['ID']) + '/' + str(
            kee)
        category_new = max_dictdetail_two['ID']
        query = {"query": {
            "bool": {"must": [{"term": {"key": f"{category_new}"}}, {"match_phrase": {"value": f"{leibiename}"}}]}}}
        # print(query)
        res = es.search(index="menusnew", body=query)
        category = res['hits']['hits'][0]['_source']['oldkey']
        if len(category) > 5:
            leibeidet = category[:3] + ';' + category[:5] + ';' + category
        elif len(category) == 5:
            leibeidet = category[:3] + ';' + category
        else:
            leibeidet = category
    except:
        leibeidetail = ''
        leibeidet = '003;00301'
    return leibeidet


def filter(result_lt):
    """
    该函数用于过滤系统中已经有了的法规
    :param result_lt: 传入列表套字典
                [data_dt = {
                            "法规标题": title,
                            "法规url": title_url,
                            "发文字号": issued_num,
                            "发布日期": issued_date
                        }]
    :return: 系统中没有的法规列表
    """
    new_result_lt = []
    for result in result_lt:
        title = result.get('法规标题')
        issued_date = result.get('发布日期')
        if not issued_date:
            issued_date = None
        try:
            # 尝试重试三次
            for attempt in range(3):
                if main_panduan(title_a=title, fm='831', issued_date=issued_date):
                    _log.info(f"法器地方法规有这条数据： {title}")
                    break  # 成功匹配，跳出循环
                else:
                    new_result_lt.append(result)
                    break  # 法规不存在，跳出循环
        except Exception as e:
            _log.error(f"判断法规存在性： {title} 时发生错误: {str(e)}")
    return new_result_lt


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
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # 返回页面内容
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
            else:
                # 如果状态码不是200，则尝试修改URL并重新请求
                _log.info(f"请求失败，状态码：{response.status_code}")
        except requests.exceptions.RequestException as e:
            _log.info(f"出错！      {e}")
            sleep = random.uniform(2, 3)
            _log.info(f"休眠{sleep}秒")
            time.sleep(sleep)
            _log.info("==========================")

    _log.info("达到最大重试次数，仍无法获取该网站内容")
    _log.info(f"网站url:  {url}")
    return None


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


def process_row_clean(title):
    """
    用于根据文章标题来筛除一些不需要的文章，包含以下关键词的标题的文章都不要
    适用于：其他文件，地区性文件(收录规范性文件、工作文件)
    :param title:包含法规标题
    :return: 如果需要则返回True
    """
    # '政策解读', '答记者问' 争议
    # 排除关键字
    excluded_keywords = {
        '公告', '通报', '通告', '公示', '资质审批名单', '征求意见稿', '备案', '面试名单',
        '培训会', '核准', '公布表', '获批', '予以备案', '备案公告', '报告', '资源包下载', '评估',
        '活动情况', '诉求清单', '聘用', '招聘启事', '人员启事', '招聘人员面试'}
    # 排除后缀
    excluded_suffixes = {
        '公告', '通报', '通告', '公示', '资质审批名单', '征求意见稿', '备案', '面试名单',
        '工作', '培训会', '核准', '公布表', '获批', '予以备案', '备案公告', '报告', '资源包下载', '评估', '活动情况',
        '诉求清单'}
    # 针对地方法规文件，不录入国务院等中央文件
    department_not_dt = {
        '国务院'
    }
    # 检查是否以排除后缀结尾
    if any(title.endswith(suffix) for suffix in excluded_suffixes):
        return False
    # 检查是否包含排除关键字
    if any(keyword in title for keyword in excluded_keywords):
        return False
    # 检查部门信息
    if any(keyword in title for keyword in department_not_dt):
        return False
    return True


def save_sql_BidDocument(sql):
    """
    用于插入数据库
    :param sql
    :return:
    """
    connect = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    # 创建游标对象
    cursor = connect.cursor()
    # sql = "INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
    # cursor.executemany(sql, all_result)
    cursor.execute(sql)
    cursor.commit()
    cursor.close()
    connect.close()


def query_sql_BidDocument(sql):
    """
    用于执行数据库查询
    :param sql: 查询语句
    :return: 查询结果
    """
    connect = pyodbc.connect(
        'DRIVER={SQL Server};SERVER=47.97.3.24,14333;DATABASE=自收录数据;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    # 创建游标对象
    cursor = connect.cursor()
    try:
        # 执行查询
        cursor.execute(sql)
        # 获取查询结果
        results = cursor.fetchall()
        # 返回查询结果
        return results
    finally:
        # 关闭游标和连接
        cursor.close()
        connect.close()


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
                # if s in not_dt or s.startswith('text-align:right'):
                #     new_styles.append(s)

            if new_styles:
                tag_s['style'] = '; '.join(new_styles)
            else:
                del tag_s['style']

    for tag in soup_ture.find_all(True):
        attrs_to_remove = ['data-index', 'id', 'class', 'align', 'type', 'new', 'times', 'lang', 'clear', 'content',
                           'http-equiv', 'name', 'rel']
        for attr in attrs_to_remove:
            # tag.attrs 包含了标签的所有属性
            if attr in tag.attrs:
                del tag[attr]
        process_style(tag)
    # 处理可能的顶级元素样式
    process_style(soup_ture)
    return soup_ture


def get_sql_menus(key, menuname):
    """
    获取数据库中指定的部门编号
    """
    connect = pyodbc.connect(
        'Driver={SQL Server};Server=47.97.3.24,14333;Database=LawEnclosure;UID=saa;PWD=1+2-3..*Qwe!@#;'
        'charset=gbk')
    # print('数据库连接成功')
    # 创建游标对象
    cursor = connect.cursor()
    sql = f"SELECT [key],[value] FROM [FddLaw5.0].[dbo].[menus] WHERE [key] LIKE N'{key}%' AND [menuname] LIKE N'%{menuname}%' and parentid like '{key}%'"
    cursor.execute(sql)
    url_list = cursor.fetchall()
    department_dict = {text: code for code, text in url_list}
    return department_dict


def department(Description, title, area_num):
    """
    匹配发布部门
    :param area_num: 地区编号
    :param Description: 全文
    :param title:  标题
    :return:
    """
    bumenall = get_sql_menus(area_num, 'lfbj_fdep_id')
    text_bumen = pq(Description).find('p[style*="right"]').text() + pq(Description).find('p[align="right"]').text()
    bumena = text_bumen + title
    values = [str(bumenall[dept]) for dept in bumenall if dept in bumena]
    values = sorted(list(set(values)), key=len)
    fabubumen = ''
    for value in values:
        if '8' in str(values):
            if value == '8' or '8' not in value:
                pass
            else:
                fabubumen += ';' + value
    if ';' not in fabubumen[1:]:
        if len(fabubumen[1:]) == 5:
            fabubumen = fabubumen[1:2] + ';' + fabubumen[1:4] + ';' + fabubumen[1:6]
        else:
            fabubumen = fabubumen[1:2] + ';' + fabubumen[1:4] + ';' + fabubumen[
                                                                      1:6] + fabubumen
    else:
        if values[-1][:5] == values[-1]:
            fabubumen = fabubumen[1:].replace(values[-1], '').replace('827;',
                                                                      f'8;827;{values[-1][:5]}')
        else:
            fabubumen = fabubumen[1:].replace('82703;', f'8;827;{values[-1][:5]};')
    if fabubumen != ';;' and ';827;' not in fabubumen:
        fabubumen = fabubumen[0] + ';' + fabubumen[:3] + ';' + fabubumen[:5] + ';' + fabubumen
    return fabubumen


def convert_chinese_date_to_numeric(date_str):
    """
    将包含汉字数字的日期字符串转换为标准的“YYYY.MM.DD”格式。

    :param date_str: 需要检测的发布日期字符串
    :return: 转换后的日期字符串
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
    converted_year = ''.join(chinese_num_map[char] for char in year if char in chinese_num_map)
    converted_parts.append(converted_year)

    # 转换月份
    month = parts[1]
    if month in month_day_map:
        converted_month = month_day_map[month]
    else:
        # 如果月份是单个汉字数字，将其转换为两位数
        converted_month = month_day_map[chinese_num_map[month]]
    converted_parts.append(converted_month)

    # 转换日期
    day = parts[2]
    if day in month_day_map:
        converted_day = month_day_map[day]
    else:
        # 如果日期是单个汉字数字，将其转换为两位数
        converted_day = month_day_map[chinese_num_map[day]]
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
        "发文字号": "",
        "发布日期": "",
        "发布部门": ""
    }
    in_lt = ["成文日期", "发布日期"]
    table_t = soup.find(['table', 'div', 'ul'], class_=["zwxl-table", "a11", "zw-table clearfix", "zwxl-head"])
    if table_t:
        tr_all = table_t.find_all('tr')
        if not tr_all:
            tr_all = table_t.find_all('div')
        if not tr_all:
            tr_all = table_t.find_all('li')
        if not tr_all:
            tr_all = table_t.find_all('span')
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
            if "发布机构" in tag_text:
                pattern = r'\[ 发布机构 \]\s*(.*)'
                match = re.search(pattern, tag_text)
                if match:
                    code = match.group(1).strip()
                    # 检查是否为空
                    if code:
                        data_dt["发布部门"] = code
        if data_dt.get('发文字号') is None or data_dt.get('发布日期') is None:
            tr_text = ''
            for tag in tr_all:
                tr_text_any = tag.get_text()
                tr_text += tr_text_any
            patterns = {
                '发文字号': r'\[ 发文字号 \]([^\[\]]+)',
                '成文日期': r'\[ 成文日期 \]\s*(\d{4}-\d{2}-\d{2})'
            }

            # 提取信息
            data_dt = {}
            for key, pattern in patterns.items():
                match = re.search(pattern, tr_text)
                if match:
                    data_dt[key] = match.group(1).strip()
    return data_dt


def match_date(zhengwen, soup):
    """
    从正文中检索出发布日期
    :param soup:
    :param zhengwen: 正文字符串
    :return:
    """
    # 关键词列表
    data_dt = soup_get_date(soup)
    tag_text = data_dt.get("发布日期")
    if tag_text:
        return tag_text
    date_lt = ["年", "月", "日"]
    soup = BeautifulSoup(zhengwen, 'html.parser')
    soup_right_all = soup.find_all(style=True)

    # 拼接日期
    date_text = ''
    for tag in soup_right_all:
        tag_text = tag.get_text().strip()
        if any(keyword in tag_text for keyword in date_lt):
            # 返回包含日期关键字的文本
            _log.info(f"从文中匹配到发布日期 {tag_text}")
            found_components = [component for component in date_lt if component in tag_text]
            if len(found_components) == len(date_lt):
                tag_text = tag_text.replace("年", ".").replace("月", ".").replace("日", "")
                tag_text = convert_chinese_date_to_numeric(tag_text)
            elif len(found_components) > 0:
                date_text += tag_text
                continue
            else:
                continue
            # 如果直接是完整日期则完整输出
            if any('\u4e00' <= char <= '\u9fff' for char in tag_text):
                # 检查字符串中是否还有汉字
                continue
            # 将输入的字符串转换为日期对象
            date_obj = datetime.strptime(tag_text, "%Y.%m.%d")
            # 格式化日期对象为所需的字符串格式
            tag_date = date_obj.strftime("%Y.%m.%d")
            return tag_date

    found_components = [component for component in date_lt if component in date_text]
    if len(found_components) == len(date_lt):
        date_text = date_text.replace("年", ".").replace("月", ".").replace("日", "")
        date_text = convert_chinese_date_to_numeric(date_text)
        # 将输入的字符串转换为日期对象
        date_obj = datetime.strptime(date_text, "%Y.%m.%d")
        # 格式化日期对象为所需的字符串格式
        tag_date = date_obj.strftime("%Y.%m.%d")
        return tag_date


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

    remove_text_lt = ['span', 'video', 'p']
    for it_t in remove_text_lt:
        # 遍历所有的对应标签
        for span in soup.find_all(it_t):
            # 如果对应标签的文本为空，则移除它
            if not span.get_text().strip():
                span.decompose()

    remove_all_lt = ['img', 'script']
    for it_a in remove_all_lt:
        # 删除所有的对应标签
        for img in soup.find_all(it_a):
            img.decompose()

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
    if is_add_right:
        # 为最终落款格式未靠右的文章添加靠右
        soup = add_right(soup, ['局', '会'])
        soup = add_right(soup, ['年', '月', '日'])
    return soup


def set_right_alignment(html_content):
    """
    本函数用于检查 HTML 中的 <p> 标签，如果标签内的文本长度不超过 30 个字符，
    并且包含关键字之一，并且不包含排除字符串之一，则将这些标签的样式设置为靠右对齐。
    如果标签已经设置了居中对齐，则不执行任何操作。

    :param html_content: HTML 内容字符串
    :return: 修改后的 HTML 内容字符串
    """
    # 关键字列表
    keywords = ['海关', '局', '会']
    special_keywords = ['年', '月', '日']

    # 排除字符串列表
    exclude_strings = ['条', '章', '解释', '指引', '服务', '通知', '违反', '布局']

    # 遍历所有 <p> 标签
    for tag in list(reversed(html_content.find_all('p')))[:-9]:
        # 获取标签的文本内容
        text = tag.get_text(strip=True)

        # 检查文本长度是否不超过 30 个字符
        if len(text) <= 30:
            # 检查文本是否包含普通关键字之一
            if any(keyword in text for keyword in keywords):
                # 检查文本是否包含排除字符串之一
                if not any(exclude_string in text for exclude_string in exclude_strings):
                    # 检查标签是否已有居中对齐样式
                    if 'text-align: center;' not in tag.get('style', ''):
                        # 设置样式为靠右对齐
                        tag['style'] = tag.get('style', '') + 'text-align: right;'
            # 检查文本是否包含特殊关键字
            elif all(keyword in text for keyword in special_keywords):
                # 检查文本是否包含排除字符串之一
                if not any(exclude_string in text for exclude_string in exclude_strings):
                    # 检查标签是否已有居中对齐样式
                    if 'text-align: center;' not in tag.get('style', ''):
                        # 设置样式为靠右对齐
                        tag['style'] = tag.get('style', '') + 'text-align: right;'
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


def main_test():
    md5 = get_md5(
        """关于印发《新疆维吾尔自治区新疆生产建设兵团市场监督管理行政处罚裁量权适用规定》《新疆维吾尔自治区新疆生产建设兵团市场监督管理行政处罚裁量基准（2024年）》的通知""")
    print(md5)
    pass


if __name__ == '__main__':
    main_test()
