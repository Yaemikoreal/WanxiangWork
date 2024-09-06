import os
import time
import random
from bs4 import BeautifulSoup, NavigableString
import hashlib
from sqlalchemy import create_engine
import logging
from query.QueryTitle import main_panduan
from Sample.分类 import get_data_from_api, key_word
import re
import pyodbc
import requests
from datetime import datetime
from pyquery.pyquery import PyQuery as pq
import jieba

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
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            if response.status_code == 200:
                # 返回页面内容
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup
        except pyodbc.OperationalError as e:
            # TODO 重庆市民政局暂用
            url = url.replace('zcwj_166256/qtwj_166259/', '')
            _log.info(f"出错！      {e}")
            sleep = random.uniform(2, 4)
            _log.info(f"休眠{sleep}秒")
            time.sleep(sleep)
            _log.info("==========================")
            if it == cl_num - 1:
                _log.info("该网站内容无法获取")
                _log.info(f"网站url:  {url}")
            continue
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


def save_sql_BidDocument(sql):
    '''
    用于插入数据库
    :param k:
    :param all_result:
    :return:
    '''
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


def determine(style):
    not_in_lt = ['font-family', 'margin-top', 'margin-bottom', 'font-size', 'line-height', 'text-indent']
    for it in not_in_lt:
        if it in style:
            return True
    return False


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
        "发文字号": None,
        "发布日期": None,
        "发布部门": None
    }
    in_lt = ["成文日期", "发布日期"]
    table_t = soup.find(['table', 'div', 'ul'], class_=["zwxl-table", "a11", "zw-table clearfix"])
    if table_t:
        tr_all = table_t.find_all('tr')
        if not tr_all:
            tr_all = table_t.find_all('div')
        if not tr_all:
            tr_all = table_t.find_all('li')
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
    for tag in soup_right_all:
        tag_text = tag.get_text().strip()
        if any(keyword in tag_text for keyword in date_lt):
            # 返回包含日期关键字的文本
            _log.info(f"从文中匹配到发布日期 {tag_text}")
            if "之日" in tag_text or len(tag_text) > 20 or len(tag_text) < 10:
                continue
            tag_text = tag_text.replace("年", ".").replace("月", ".").replace("日", "")
            tag_text = convert_chinese_date_to_numeric(tag_text)
            if any('\u4e00' <= char <= '\u9fff' for char in tag_text):
                # 检查字符串中是否还有汉字
                continue
            # 将输入的字符串转换为日期对象
            date_obj = datetime.strptime(tag_text, "%Y.%m.%d")
            # 格式化日期对象为所需的字符串格式
            formatted_date = date_obj.strftime("%Y.%m.%d")
            return formatted_date
    return tag_text


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
    # url = 'https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/xzgfxwj/sfzggwxzgfxwj/'
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    # }
    # soup = fetch_url(url, headers)
    # aaa = '安顺市人民政府关于印发安顺市市级储备粮管理办法的通知'
    # ddd = '''各县、自治县、区人民政府（管委会），市政府各工作部门、各直属事业单位，市属国有企业：现将《安顺市市级储备粮管理办法》印发给你们，请认真抓好贯彻落实。安顺市人民政府2023年9月5日（此件公开发布）安顺市市级储备粮管理办法第一章  总    则第一条  为加强市级储备粮管理，保障市级储备粮数量真实、质量良好和储存安全，有效发挥市级储备粮的宏观调控作用，维护安顺粮食市场稳定，依据《粮食流通管理条例》《贵州省粮食安全保障条例》《贵州省地方储备粮管理办法》《贵州省地方储备粮轮换管理办法（试行）》《贵州省政府储备粮食仓储管理办法（试行）》《贵州省粮食收购管理办法》等有关规定，结合安顺实际，制定本办法。第二条  本办法所称市级储备粮，是指市人民政府储备用于调节全市粮食供需平衡、稳定粮食市场以及应对重大自然灾害、重大卫生事件和其他突发事件等情况的原粮、成品粮、食用植物油和大豆等。第三条  本市行政区域内市级储备粮的计划、储存、轮换、动用和监督管理等活动，适用本办法。第四条  未经市人民政府批准，任何单位和个人不得擅自动用市级储备粮。第五条  市发展改革委（市粮食和物资储备局）负责市级储备粮行政管理，对市级储备粮的数量、质量和储存安全实施监督检查。第六条  市财政局会同市发展改革委（市粮食和物资储备局）负责安排并及时拨付市级储备粮的贷款利息、保管费用和轮换费（包括轮换过程中产生的费用和轮换价差）等财政补贴，对市级储备粮有关财务管理工作实施监督检查。第七条  农发行安顺分行及其分支机构按照国家有关规定，及时、足额发放市级储备粮所需贷款，贷款资金实行封闭运行，并对发放的贷款实施信贷监管。第八条  承储市级储备粮的企业应具有独立法人资格（以下简称承储企业），建立健全内控管理制度，按照“谁储粮、谁负责，谁坏粮、谁担责”的原则，做到储备与经营分开，规范管理，对市级储备粮的数量、质量和储存安全负责。第九条  建立安顺市粮食储备管理工作联席会议制度，联席会议由市发展改革委（市粮食和物资储备局）召集，市财政局、市市场监管局、农发行安顺分行为成员，负责研究市级储备粮管理中的重要事项。第二章  计    划第十条  按照省下达我市地方储备粮计划，根据全市粮食宏观调控需要，由市发展改革委（市粮食和物资储备局）会同市财政局、农发行安顺分行制定市级储备粮分解计划，报市人民政府批准后执行。第十一条  各县（区）人民政府（管委会）根据应急供应需要，建立一定规模的成品粮油储备。市人民政府所在地西秀区人民政府和安顺经开区管委会建立不低于城镇常住人口10天市场供应量的成品粮油储备，其他县（区）建立不低于城镇常住人口3天市场供应量的成品粮油储备。第三章  储    存第十二条  市级储备粮的储存品种应当按照省级安排，符合安顺消费需求，以稻谷、小麦、玉米、大豆、菜籽油等为主。其中，稻谷和小麦两大口粮品种储备比例应达储备规模的70%以上。市发展改革委（市粮食和物资储备局）、市财政局、农发行安顺分行应当根据市场消费需求，适时调整储备粮品种结构。第十三条  依据《贵州省政府储备粮食仓储管理办法（试行）》规定，承储库点应当具备以下条件：（一）仓房、油罐符合《粮油储藏技术规范》要求；（二）具有与粮油储存功能、仓（罐）型、进出库（罐）方式、粮油品种、储存周期等相适应的粮食装卸、输送、清理、计量、储藏、病虫害防治等设施设备；配备必要的防火、防盗、防洪、防雷、防冰雪等安全设施设备；支持控温储藏，有能力达到低温或者准低温储藏功效的可优先考虑；（三）具有符合国家标准的检测储备粮质量等级和储存品质必需的检测仪器设备和检化验室；具有检测粮油储存期间粮食温度、水分、害虫密度等条件；具有粮情测控系统、机械通风系统、环流熏蒸系统和适合当地气候环境条件的其他保粮技术；（四）具有与地方储备粮储存保管任务相适应，经过专业培训，掌握相应知识和技能并取得从业资格证书的仓储管理、质量检验等专业技术人员；（五）根据国家、省、市相关规定需要具备的其他条件。第十四条  承储企业应当加强仓储设施、质量检验保障能力建设和维护，推进仓储科技创新和使用，提高市级储备粮安全保障能力。使用政府性资金建设的地方储备粮仓储等设施，任何单位和个人不得擅自处置或者变更用途。第十五条  依据《贵州省地方储备粮管理办法》规定承储企业不得有下列行为：（一）擅自动用市级储备粮;（二）虚报、瞒报市级储备粮数量;（三）在市级储备粮中掺杂掺假、以次充好;（四）擅自串换品种、变更储存地点、仓号、油罐;（五）以市级储备粮和使用政府性资金建设的地方储备粮仓储等设施办理抵质押贷款、提供担保或者清偿债务，进行期货实物交割;（六）挤占、挪用、克扣财政补贴、信贷资金;（七）延误轮换或者管理不善造成市级储备粮霉坏变质;（八）以低价购进高价入账、高价售出低价入账，以旧粮顶替新粮、虚报损耗、虚列费用、虚增入库成本等手段套取差价，骗取市级储备粮的贷款和财政补贴;（九）法律法规规定的其他行为。第十六条  承储企业被依法撤销、解散或者宣告破产的，其储存的市级储备粮，由市发展改革委（市粮食和物资储备局）会同市财政局、农发行安顺分行按照本办法第十三条的要求调出另储。第十七条  承储企业应当建立市级储备粮质量安全档案，如实记录粮食质量安全情况。储存周期结束后，质量安全档案保存期不少于5年。第十八条  承储企业应当执行国家、省和市储备粮管理的有关规定，执行国家粮油质量标准和储藏技术规范。第十九条  承储企业储存市级储备粮应区分不同品种、不同收获年度、不同产地、不同性质，严格按照国家、省、市有关储备粮管理规定进行管理，做到实物、专卡、保管账“账实相符”、保管账、统计账、会计账“账账相符”；数量、品种、质量、地点“四落实”，实行专人保管、专仓储存、专账记载；确保市级储备粮数量真实、质量良好、储存安全、管理规范。储存周期结束后，保管总账、分仓保管账保存期不少于5年。第二十条  承储企业应当遵守安全生产相关法律法规和标准规范，严格执行《粮油储存安全责任暂行规定》和《粮油安全储存守则》《粮库安全生产守则》，落实安全生产责任制，制定安全生产事故防控方案或应急预案，配备必要的安全防护设施设备，建立健全储备粮防火、防盗、防汛等安全生产管理制度，定期组织开展安全生产检查，加强职工安全生产教育和培训，确保市级储备粮储存安全。承储企业在市级储备粮承储期间发生安全生产事故的，应当及时处置，并向市发展改革委（市粮食和物资储备局）、库点所在县（区）粮食行政管理部门和应急管理部门报告。第二十一条  市级储备粮储存期间，承储企业按照每季度检测1次的要求对质量指标和储存品质指标进行检验。市粮油质量检验中心每年对市级储备粮至少开展1次全面抽检。第四章  轮    换第二十二条  市级储备粮以储存粮食品质指标为依据，以储存年限为参考，原则上小麦每4年轮换一次，中晚籼稻谷每3年轮换一次，粳稻谷、玉米、食用植物油每2年轮换一次，大豆及杂粮每1年轮换一次。第二十三条  根据市级储备粮储存品质状况，结合储存年限，经市粮食储备管理工作联席会议审核或由市发展改革委（市粮食和物资储备局）、市财政局和农发行安顺分行联合发文，制定下一年度轮换计划。市级储备粮轮换工作由承储企业具体组织实施，并及时向有关部门报告轮换情况。第二十四条  市级储备粮轮换应当遵循公开、公平、公正、透明原则，原则上通过公益性专业交易平台进行公开竞价交易。必要时经市发展改革委（市粮食和物资储备局）会同市财政局和农发行安顺分行批准后，可采取直接收购、邀标竞价销售等方式进行。第二十五条  市级储备粮轮换架空期不得超过4个月。因客观原因需要延长架空期的，经市发展改革委（市粮食和物资储备局）、市财政局和农发行安顺分行联合批准，最多可延长2个月，延长期内承储企业不享受相应的保管费用补贴。第二十六条  为避免超架空期轮换，承储企业应当加强对市级储备粮轮换工作的调度，按月向市发展改革委（市粮食和物资储备局）、市财政局和农发行安顺分行报送轮换情况。承储企业要积极开展轮换工作，按时完成市级储备粮轮换计划。第二十七条  承储企业在执行轮换计划时，应加强粮油市场价格行情调研，选择最佳时机开展竞价销售和采购，最大限度减少轮换价差亏损。第二十八条  市级储备粮保管自然损耗定额为：原粮：储存6个月以内的，不超过0.1%；储存6个月以上12个月以内的，不超过0.15%；储存12个月以上的，累计不超过0.2%（不得按年叠加）;食用植物油：储存6个月以内的，不超过0.08%；储存6个月以上12个月以内的，不超过0.1%；储存12个月以上的，累计不超过0.12%（不得按年叠加）;油料：储存6个月以内的，不超过0.15%；储存6个月以上12个月以内的，不超过0.2%；储存12个月以上的，不超过0.23%（不得按年叠加）。第二十九条  市级储备粮轮换过程中，定额内损失损耗以及因自然灾害等不可抗力造成损失损耗由市发展改革委（市粮食和物资储备局）会同市财政局据实核销。超定额损耗或因经营管理不善造成损失由承储企业承担。第三十条  实行市级储备粮验收检验制度。承储企业采购储备粮，应当按国家标准和规定进行质量安全检验。储备粮采购入库平仓结束后，由市发展改革委（市粮食和物资储备局）委托有资质的粮食检验机构进行入库验收检验，验收检验包括常规质量指标、储存品质指标和食品安全指标，检验合格后方可作为市级储备粮进行验收。对不符合储备粮质量安全要求和有关规定，经整理后仍不达标的，不得入库。入库粮食水分应符合安全水分要求。第三十一条  实行市级储备粮轮换出库检验制度。市级储备粮出库承储企业委托有资质的粮食检验机构进行检验，检验结果作为出库质量依据。未经质量安全检验的粮食不得销售出库，出库粮食应附检验报告原件或复印件。出库检验项目应包括常规质量指标和食品安全指标。储存期间施用过储粮药剂且未满安全间隔期的，还应增加储粮药剂残留检验，检验结果超标的应暂缓出库。第五章  资    金第三十二条  任何单位和个人不得以任何理由及方式骗取、挤占、截留、挪用市级储备粮贷款及利息、保管费用和合理轮换费用等财政补贴。第三十三条  市级储备粮的入库成本由市财政局会同市发展改革委（市粮食和物资储备局）、农发行安顺分行进行核定，入库成本一经核定，不得擅自变更。第三十四条  市级储备粮的贷款利息实行据实结算，专户管理、专款专用，接受开户行的信贷监管，保证市级储备粮资金封闭运行。第三十五条  市级储备粮保管费、轮换费实行定额包干。其中，市级储备粮（原粮）保管费每年100元／吨，食用植物油保管费每年300元／吨；市级储备粮（原粮）轮换价差补贴标准为750元／吨，食用植物油轮换价差补贴标准为700元／吨。在市场粮油价格大幅上涨等特殊情况下，若定额包干补贴不足以弥补价差亏损时，采取“一事一议”的方式，通过提高轮换价差补贴标准或对轮换亏损进行据实补贴等办法加以解决。第三十六条  市级储备粮轮换贷款实行购贷销还，封闭运行。市级储备粮轮出销售款应当及时、全额偿还农业发展银行贷款。采取先购后销轮换方式，由农发行安顺分行及其分支机构先发放轮换贷款，待验收入库转为市级储备粮后，及时发放市级储备粮贷款，同时足额收回相应的轮换贷款；采取先销后购轮换方式，销售后收回贷款，轮入所需资金，由农发行安顺分行及其分支机构及时、足额发放市级储备粮贷款。对于轮换后成本调整的，按照重新核实的成本发放贷款。第六章  动    用第三十七条  市发展改革委（市粮食和物资储备局）要加强粮食市场动态监测，按照《安顺市粮食应急预案》要求，会同市财政局提出市级储备粮动用方案，报市人民政府批准，由市发展改革委（市粮食和物资储备局）会同市财政局组织实施。动用方案应当包括动用市级储备粮的品种、数量、质量、价格、使用安排、运输保障等内容。应急动用市级储备粮产生的价差收入扣除相关费用后应当上缴市财政局，产生的价差亏损和相关费用，由市财政局据实补贴。第三十八条  出现下列情况之一的，市人民政府可以批准动用市级储备粮：（一）全市或者部分县（区）粮食明显供不应求或者市场价格异常波动的；（二）发生重大自然灾害、重大公共卫生事件或者其他突发事件的；（三）市人民政府认为需要动用市级储备粮的其他情形。第三十九条  动用地方储备粮应当首先动用县级储备粮。县级储备粮不足时，由县级人民政府向市人民政府申请动用市级储备粮。市级储备粮不足的，由市人民政府向省人民政府申请动用省级储备粮。紧急情况下，市人民政府直接决定动用市级储备粮并下达动用命令。原则上，储备动用后在12个月内完成等量补库。第四十条  市人民政府有关部门和县（区）人民政府（管委会）对市级储备粮动用命令应当给予支持、配合。任何单位和个人不得拒绝执行或者擅自改变市级储备粮动用方案。第七章  监督检查第四十一条  按照《贵州省地方储备粮管理办法》规定，市发展改革委（市粮食和物资储备局）、市财政局等部门单位，按照各自职责，对执行本办法及国家和省储备粮管理规章制度进行监督检查，并行使下列职权：（一）进入承储企业检查市级储备粮的数量、质量和储存安全；（二）向有关单位和人员了解市级储备粮采购、销售、轮换计划、动用及有关财务执行等情况；（三）调阅、复印市级储备粮经营管理的有关账簿、原始凭证、电子数据等有关资料；（四）对承储企业的法定代表人、负责人或其他工作人员进行问询；（五）法律法规规定的其他职权。第四十二条  承储企业应当积极配合市发展改革委（市粮食和物资储备局）、市财政局等部门依法开展的监督检查工作。任何单位和个人不得拒绝、阻挠、干涉市发展改革委（市粮食和物资储备局）、市财政局等监督检查人员履行监督检查职责。第四十三条  市发展改革委（市粮食和物资储备局）、市财政局等相关部门在监督检查中，一旦发现市级储备粮数量、质量、储存安全等方面存在问题，依法依规进行处理。第四十四条  承储企业应当建立健全内部控制和合规管理制度，加强对市级储备粮的管理，有效防范和控制粮食储备运营风险。对危及市级储备粮储存安全的重大问题，应当立即采取有效措施妥善处理，并及时报告市发展改革委（市粮食和物资储备局）、市财政局及农发行安顺分行。第四十五条  承储企业违反《粮食流通管理条例》《贵州省地方储备粮管理办法》《贵州省粮食收购管理办法》等规定的，由市发展改革委（市粮食和物资储备局）、市财政局按照各自职责依法依规查处。第八章  附    则第四十六条  本办法自印发之日起施行。'''
    # catagroy_select(ddd, aaa)

    dd = '''<p style="text-align:center">
    重庆市粮食局 重庆市财政局
</p>
<p style="text-align:center">
    关于印发《重庆市政策性粮食购销违法违规
</p>
<p style="text-align:center">
    行为举报奖励实施细则（试行）》的通知
</p>
<p style="text-align:center">
    渝粮规范〔2023〕2号
</p>
<p>
    各区县（自治县）发展改革委、财政局，两江新区经济运行局、财政局，西部科学城重庆高新区改革发展局、财政局，万盛经开区发展改革局、财政局：
</p>
<p>
    为动员社会力量参与政策性粮食购销领域监督，鼓励举报政策性粮食购销违法违规行为，根据《粮食流通管理条例》《中央储备粮管理条例》《重庆市地方粮食储备管理办法》等法律法规，依据国家粮食和物资储备局《政策性粮食购销违法违规行为举报奖励办法（试行）》（国粮执法规〔2023〕144号），结合我市实际，制定《重庆市政策性粮食购销违法违规行为举报奖励实施细则（试行）》，现印发给你们，请认真遵照执行。
</p>
<p style="text-align:right">
    重庆市粮食局 重庆市财政局
</p>
<p style="text-align:right">
    2023年12月31日
</p>
<p style="text-align:center">
    重庆市政策性粮食购销违法违规行为
</p>
<p style="text-align:center">
    举报奖励实施细则（试行）
</p>
<p>
    第一条 为动员社会力量参与政策性粮食购销领域监管，鼓励社会公众积极举报政策性粮食购销违法违规行为，根据《粮食流通管理条例》《中央储备粮管理条例》《重庆市地方粮食储备管理办法》等法律法规，依据《政策性粮食购销违法违规行为举报奖励办法（试行）》（国粮执法规〔2023〕144号），结合我市实际，制定本实施细则。
</p>
<p>
    第二条 自然人（以下称举报人）可通过12325等热线电话、政府网站、信函以及其他渠道，向各级粮食行政管理部门举报。
</p>
<p>
    12325热线电话举报线索的接收受理、办理等事项，按《12325全国粮食和物资储备监管热线举报处理规定》（国家粮食和物资储备局公告2021年第5号）等规定处理。
</p>
<p>
    重庆市各级粮食行政管理部门负责本行政区域内政策性粮食购销违法违规行为举报奖励工作。举报奖励工作依法保护举报人合法权益，实行自愿领取、奖励适当的原则。
</p>
<p>
    第三条 举报人向粮食行政管理部门反映从事政策性粮食购销经营活动涉嫌违反《粮食流通管理条例》《中央储备粮管理条例》《重庆市地方粮食储备管理办法》等规定的行为，以及竞买政策性粮食时恶意违约等违反合同规定的行为，且属于重庆市各级粮食行政部门管辖范围，经查证属实应予奖励的，适用本实施细则。
</p>
<p>
    第四条 奖励举报人须同时符合下列条件：
</p>
<p>
    （一）有明确的被举报对象和具体违法违规线索，并提供了有效证据；
</p>
<p>
    （二）举报事项事先未被重庆市各级粮食行政管理部门掌握，或者虽有所掌握，但举报人提供的情况更为具体详实；
</p>
<p>
    （三）举报事项经查证属实；
</p>
<p>
    （四）举报人愿意得到举报奖励，并提供可供核查且真实有效的身份信息、联系方式等；
</p>
<p>
    （五）其他依法依规应予奖励的必备条件。
</p>
<p>
    第五条 有下列情形之一的，不予奖励或者不予重复奖励：
</p>
<p>
    （一）举报人为重庆市各级粮食行政管理部门、国家粮食和物资储备局垂直管理局工作人员或者其他具有法定职责人员的；
</p>
<p>
    （二）在收到举报前，政策性粮食违法违规行为人已主动供述本人及其同案人员的违法违规事实，或者在被调查处理期间检举揭发其他违法违规行为的；
</p>
<p>
    （三）粮食行政管理部门对举报事项作出处理决定前，举报人主动撤回举报的；
</p>
<p>
    （四）举报线索移送其他部门处理的；
</p>
<p>
    （五）举报人就同一违法违规行为多处、多次举报的，不予重复奖励；
</p>
<p>
    （六）举报人身份无法确认或者无法与举报人取得联系的；
</p>
<p>
    （七）举报前，相关政策性粮食违法违规行为已进入诉讼等法定程序的；
</p>
<p>
    （八）其他依法依规不予奖励的情形。
</p>
<p>
    第六条 举报奖励发放规则：
</p>
<p>
    （一）同一违法违规行为由两个及两个以上举报人分别举报的，奖励最先举报人，举报次序以粮食行政管理部门受理举报的登记时间为准；
</p>
<p>
    （二）两个及两个以上举报人联名举报同一违法违规行为的，按照同一举报给予奖励，奖励资金由举报人自行协商分配；
</p>
<p>
    （三）在举报线索调查中发现新的违法违规行为线索的，不对新的违法违规行为线索给予奖励；
</p>
<p>
    （四）国家粮食和储备行政管理部门规定的其他奖励规则。
</p>
<p>
    第七条 举报奖励由查处举报案件的粮食行政管理部门负责，对符合奖励条件的举报人，综合考虑查实违法违规行为的危害程度、对国家造成的经济损失、线索质量以及行政处罚罚款金额等因素，按照以下标准给予一次性资金奖励：
</p>
<p>
    （一）罚款金额在15万元以下的，按1500元奖励；
</p>
<p>
    （二）罚款金额在15万元以上的，50万元以下的，按罚款金额的1%奖励；
</p>
<p>
    （三）罚款金额在50万元以上的，200万元以下的，按罚款金额的2%奖励；
</p>
<p>
    （四）罚款金额在200万元以上的，500万元以下的，按罚款金额的3%奖励；
</p>
<p>
    （五）罚款金额在500万元以上的，按150000元奖励。
</p>
<p>
    对于同一举报涉及两个及两个以上的粮食行政管理部门管辖、分别由两个及两个以上的粮食行政管理部门调查处理的，由查处举报案件的粮食行政管理部门分别根据本部门的举报线索查实处理情况进行奖励。
</p>
<p>
    第八条 举报奖励资金按程序纳入重庆市各级粮食行政管理部门年度预算。举报奖励资金应当使用非现金的方式兑付，按国库集中支付规定办理。同时，接受纪检、审计和财会等相关部门监督。
</p>
<p>
    第九条 对政策性粮食购销违法违规行为作出处理决定后30个工作日内，由查处举报案件的粮食行政管理部门启动奖励程序，并在作出奖励决定之日起10个工作日内以书面、邮件、电话等方式告知举报人。
</p>
<p>
    举报人放弃奖励的，终止奖励程序。
</p>
<p>
    第十条 举报人应当在收到领取奖励通知之日起30个工作日内，凭本人有效身份证明领取奖励。委托他人代领的，受托人须同时持有举报人授权委托书、举报人和受托人的有效身份证明。举报人逾期未领取奖励的，视为主动放弃。联名举报的举报人应当推举一名代表领取奖励。
</p>
<p>
    第十一条 重庆市各级粮食行政管理部门在办理举报奖励资金发放时，应当严格审核。举报奖励资金发放后，发现存在伪造材料、隐瞒事实等情况骗取举报奖励的，或者存在其他不符合领取奖励的情形，发放奖励的粮食行政管理部门查实后有权收回举报奖励资金，并依法依规依职责追究当事人相应责任，涉嫌犯罪的，移送司法机关。
</p>
<p>
    第十二条 举报人应当对举报内容及其提供材料的真实性负责，捏造、歪曲事实或者诬告陷害他人的，应当依法承担相关法律责任。
</p>
<p>
    第十三条 重庆市各级粮食行政管理部门应当严格为举报人保密，不得以任何方式泄露举报人身份等相关信息。粮食行政管理部门相关工作人员泄露举报人信息的，依规依纪依法给予严肃处理。
</p>
<p>
    第十四条 本实施办法中涉及的“以上”包含本数，“以下”不包含本数。
</p>
<p>
    第十五条 本实施细则自发布之日起施行，有效期5年。
</p>
<p>
    附件：1．重庆市政策性粮食购销违法违规行为举报奖励审批表
</p>
<p>
    2．重庆市政策性粮食购销违法违规行为举报奖励通知书
</p>
<p>
    3．重庆市放弃政策性粮食购销违法违规行为举报奖励资金声明书
</p>
<p>
    4．重庆市领取政策性粮食购销违法违规行为举报奖励资金授权委托书
</p>
<p>
    附件1
</p>
<p style="text-align:center">
    重庆市政策性粮食购销违法违规行为举报奖励审批表
</p>
<p>
    审批表编号： &nbsp;审批单位：
</p>
<table align="center" border="1" cellspacing="0" class="Table">
    <tbody>
        <tr class="firstRow">
            <td>
                <p style="text-align:center">
                    举报人姓名
                </p>
            </td>
            <td></td>
            <td>
                <p style="text-align:center">
                    身份证号码或
                </p>
                <p style="text-align:center">
                    其他身份识别信息
                </p>
            </td>
            <td></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    受举报时间
                </p>
            </td>
            <td></td>
            <td>
                <p style="text-align:center">
                    举报人联系方式
                </p>
            </td>
            <td></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    举报内容
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    查办结果
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    核查部门
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    行政处罚金额
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    奖励金额
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    承办部门和人员
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    承办部门
                </p>
                <p style="text-align:center">
                    负责人意见
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    财务部门
                </p>
                <p style="text-align:center">
                    负责人意见
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    承办部门
                </p>
                <p style="text-align:center">
                    分管局领导意见
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    局主要负责
                </p>
                <p style="text-align:center">
                    领导意见
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
        <tr>
            <td>
                <p style="text-align:center">
                    备 注
                </p>
            </td>
            <td colspan="3"></td>
        </tr>
    </tbody>
</table>
<p>
    注：该表一式3份，由粮食行政管理部门填写，财务、存档各1份。
</p>
<p>
    附件2
</p>
<p style="text-align:center">
    重庆市政策性粮食购销违法违规行为
</p>
<p style="text-align:center">
    举报奖励通知书
</p>
<p style="text-align:right">
    <span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>举报奖字〔 〕<span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>号
</p>
<p>
    <span style="text-decoration:underline;"> </span>：
</p>
<p>
    根据《重庆市政策性粮食购销违法违规行为举报奖励实施细则（试行）》（渝粮规范〔2023〕2号）文件，决定对<span style="text-decoration:underline;"> </span>你举报的<span style="text-decoration:underline;"> </span>案件（案件编号：<span style="text-decoration:underline;"> </span>）给予奖励资金<span style="text-decoration:underline;"> </span>元（大写：<span style="text-decoration:underline;"> </span>）。
</p>
<p>
    请在接到本通知书后的30个工作日内，提供有效身份证明、银行账户信息（开户银行名称及账号）等。如果委托他人代领的，受托人还应当同时持有举报人授权委托书、举报人和受托人的有效身份证明。联名举报的举报人应当推举一名代表，此代表需持所有举报人授权的授权委托书。
</p>
<p>
    逾期未办理身份确认手续的，视为自动放弃。
</p>
<p>
    联系人： 联系电话：
</p>
<p>
    （盖章）
</p>
<p>
    <span style="text-decoration:underline;"> </span>年<span style="text-decoration:underline;"> </span>月<span style="text-decoration:underline;"> </span>日
</p>
<p>
    注：此文书一式3份，举报人、财务、存档各1份。
</p>
<p>
    附件3
</p>
<p style="text-align:center">
    重庆市放弃政策性粮食购销违法违规行为
</p>
<p style="text-align:center">
    举报奖励资金声明书
</p>
<p>
    本人<span style="text-decoration:underline;"> </span>，身份证号：<span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>，于<span style="text-decoration:underline;"> </span>年<span style="text-decoration:underline;"> </span>月<span style="text-decoration:underline;"> </span>日举报的<span style="text-decoration:underline;"> </span>案件（案件编号：<span style="text-decoration:underline;"> </span>），<span style="text-decoration:underline;"> </span>根据《重庆市政策性粮食购销违法违规行为举报奖励实施细则（试行）》（渝粮规范〔2023〕2号）文件，已通知给予我本人举报奖励的资金<span style="text-decoration:underline;"> </span>元（大写：<span style="text-decoration:underline;"> </span>），本人郑重申明放弃。
</p>
<p>
    申明人（签字并盖手印）：
</p>
<p>
    联系电话：
</p>
<p>
    年月日
</p>
<p>
    注：此文书一式3份，举报人、财务、存档各1份。此文书空白处由举报人手工填写。
</p>
<p>
    附件4
</p>
<p style="text-align:center">
    重庆市领取政策性粮食购销违法违规行为
</p>
<p style="text-align:center">
    举报奖励资金授权委托书
</p>
<p>
    本人<span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>，身份证号：<span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>，于<span style="text-decoration:underline;"> </span>年<span style="text-decoration:underline;"> </span>月<span style="text-decoration:underline;"> </span>日举报的<span style="text-decoration:underline;"> </span>案件（案件编号： <span style="text-decoration:underline;"> </span>），经<span style="text-decoration:underline;"> </span>根据《重庆市政策性粮食购销违法违规行为举报奖励实施细则（试行）》（渝粮规范〔2023〕2号）文件，已通知给予我本人举报奖励资金<span style="text-decoration:underline;"> </span>元（大写： <span style="text-decoration:underline;"> </span>）。本人因故无法亲自办理奖励资金领取，现委托<span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>，身份证号：<span style="text-decoration:underline;"> </span>为我办理有关奖励资金领取手续。
</p>
<p>
    委托人（签字并盖手印）：
</p>
<p>
    联系电话：
</p>
<p>
    受托人（签字并盖手印）：
</p>
<p>
    联系电话：
</p>
<p>
    <span style="text-decoration:underline;"> </span><span style="text-decoration:underline;"> </span>年<span style="text-decoration:underline;"> </span>月<span style="text-decoration:underline;"> </span>日
</p>
<p>
    注：此文书一式4份，委托人、受托人、财务、存档各1份。此文书空白处由委托人手工填写。
</p>'''
    aa = '重庆市粮食局 重庆市财政局关于印发重庆市政策性粮食购销违法违规行为举报奖励实施细则（试行）的通知'
    cc = department(dd, aa, '831')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
    }
    annex_get('https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/202408/W020240827391403402403.docx',
              '关于印发《重庆市深入推进快递包装绿色转型实施方案》的通知.docx', headers=headers)
    pass


if __name__ == '__main__':
    main_test()
