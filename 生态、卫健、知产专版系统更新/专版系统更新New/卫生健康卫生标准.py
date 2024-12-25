import time
import random
import re
from botpy import logging as botpy_logging
import pandas as pd
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions
from 附件下载程序 import public_down
from 预处理 import selectsql, insertsql, intDate, gettimestr

# 设置日志记录
_log = botpy_logging.get_logger()

# 定义常量
BASE_URL = 'http://www.nhc.gov.cn/wjw/wsbzxx/'  # 基础URL
URL_TEMPLATE = BASE_URL + 'wsbz{suf}.shtml'  # URL模板，用于生成分页链接
URL_ROOT = 'http://www.nhc.gov.cn'  # 网站根URL
CATEGORY = '卫生标准'  # 数据类别
DATE_CUTOFF = 20200728  # 日期截止点，只处理此日期之后的数据
DOWNLOAD_PATH = r'E:/JXdata/生态环境依法行政法律资源应用支持系统/卫生健康依法行政法律资源应用支持系统/{}/'.format(CATEGORY)  # 附件下载路径
EXCEL_SAVE_PATH = r'E:/JXdata/专版系统更新标准收录/收录数据/卫生健康标准_{}.xlsx'  # Excel文件保存路径
DATABASE_TABLE = '[自收录数据].[dbo].[wj-卫计局]'  # 数据库表名
PUBLISH_DEPARTMENT = '卫生健康委员会'

# 创建浏览器对象并设置选项
options = ChromiumOptions()
options.headless = True  # 设置无头模式
browser = ChromiumPage(options)


def fetch_page_content(page_index):
    """
    根据页面索引获取页面内容。

    :param page_index: 页面索引，从0开始
    :return: 解析后的BeautifulSoup对象
    """
    url = URL_TEMPLATE.format(suf=f'_{page_index}' if page_index > 0 else '')
    browser.get(url)
    browser.wait(1.5)
    return BeautifulSoup(browser.html, "html.parser")


def get_tab_content(href):
    """
    获取指定链接的内容。

    :param href: 链接
    :return: 完整链接和解析后的BeautifulSoup对象
    """
    full_url = URL_ROOT + href
    browser.get(full_url)
    browser.wait(1.5)
    return full_url, BeautifulSoup(browser.html, "html.parser")


def process_row(row_element, date_cutoff):
    """
    处理表格中的每一行数据。

    :param row_element: 表格行元素
    :param date_cutoff: 日期截止点
    :return: 如果成功处理返回数据字典，否则返回False
    """
    link = row_element.find('a').get('href')
    title = row_element.find('a').get('title')
    publish_date = intDate(row_element.find_all('td')[3].text)
    implementation_date = intDate(row_element.find_all('td')[4].text)

    _log.info(f"[{title}] 正在处理")

    if publish_date <= date_cutoff:
        _log.info("发布日期早于截止日期，跳过该行")
        _log.info("====" * 20)
        return False

    sql_query = f"SELECT * FROM {DATABASE_TABLE} WHERE [标题] LIKE '{title}%'"
    if selectsql(sql_query):
        _log.info('数据库已存在该数据!')
        _log.info("====" * 20)
        return False

    full_url, soup = get_tab_content(link)
    attachments = []

    for attachment in soup.find_all('a', href=re.compile(
            r'.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz)+$')):
        file_link = attachment.get('href')
        full_file_link = f"{full_url.rsplit('/', 1)[0]}/{file_link}"
        file_name = file_link.split('/')[-1]

        public_down(full_file_link, DOWNLOAD_PATH + file_name)
        attachment['href'] = f'/datafolder/卫生健康依法行政法律资源应用支持系统/{CATEGORY}/{file_name}'
        attachments.append(attachment['href'])

    if attachments:
        # 处理日期格式
        publish_date = f"{str(publish_date)[:4]}.{str(publish_date)[4:6]}.{str(publish_date)[6:]}"
        implementation_date = f"{str(implementation_date)[:4]}.{str(implementation_date)[4:6]}.{str(implementation_date)[6:]}"
        attachments_str = str(attachments).replace("'", '"')
        unique_id = f"wjj{gettimestr()}{random.randint(0, 9)}"
        insert_sql = f"INSERT INTO {DATABASE_TABLE} ([标题], [类别], [发布日期], [实施日期], [全文], [url], [附件], [唯一标志],[发布部门]) VALUES ('{title}', '{CATEGORY}', '{publish_date}', '{implementation_date}', '', '{full_url}', '{attachments_str}', '{unique_id}','{PUBLISH_DEPARTMENT}')"
        insertsql(insert_sql)
        data_dict = {
            "标题": title,
            "类别": CATEGORY,
            "发布日期": publish_date,
            "实施日期": implementation_date,
            "全文": '',
            "url": full_url,
            "附件": attachments_str,
            "唯一标志": unique_id
        }
        _log.info("====" * 20)
        return data_dict
    return False


def main():
    """
    主函数，负责组织整个流程，包括初始化Excel文件、遍历页面、处理每一行数据以及发送通知。
    """
    data_list = []
    timestamp = time.strftime('%Y%m%d', time.localtime(time.time()))

    try:
        for page_index in range(10):  # 可根据需要调整页数
            _log.info(f"处理第[{page_index + 1}]页")
            soup = fetch_page_content(page_index)
            for row in soup.find_all('tr', bgcolor="#ffffff"):
                data_dict = process_row(row, DATE_CUTOFF)
                if data_dict:
                    data_list.append(data_dict)
            _log.info("====" * 20)

        if data_list:
            data_df = pd.DataFrame(data_list)
            file_path = EXCEL_SAVE_PATH.format(timestamp)
            data_df.to_excel(file_path, index=False)

    except Exception as e:
        _log.error(e)
    finally:
        browser.quit()


if __name__ == '__main__':
    main()