import time
import random
import re
from botpy import logging
import pandas as pd
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions
from 附件下载程序 import public_down
from 预处理 import selectsql, insertsql, intDate, gettimestr
_log = logging.get_logger()
# 定义常量
BASE_URL = 'http://www.nhc.gov.cn/wjw/wsbzxx/'  # 基础URL
URL_TEMPLATE = BASE_URL + 'wsbz{suf}.shtml'  # URL模板，用于生成分页链接
URL_ROOT = 'http://www.nhc.gov.cn'  # 网站根URL
CATEGORY = '卫生标准'  # 数据类别
DATE_CUTOFF = 20200728  # 日期截止点，只处理此日期之后的数据
DOWNLOAD_PATH = r'E:/JXdata/生态环境依法行政法律资源应用支持系统/卫生健康依法行政法律资源应用支持系统/{}/'.format(CATEGORY)  # 附件下载路径
EXCEL_SAVE_PATH = r'E:/JXdata/专版系统更新标准收录/收录数据/卫生{}.xlsx'  # Excel文件保存路径
DATABASE_TABLE = '[自收录数据].[dbo].[wj-卫计局]'  # 数据库表名


# 创建浏览器对象并设置选项
# co = ChromiumOptions().set_browser_path(r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
co = ChromiumOptions()
# 设置无头模式
co.headless(False)
wd = ChromiumPage(co)


def fetch_page_content(page_index):
    """
    根据页面索引获取页面内容。

    :param page_index: 页面索引，从0开始
    :return: 解析后的BeautifulSoup对象
    """
    url = URL_TEMPLATE.format(suf='_' + str(page_index) if page_index > 0 else '')  # 构建页面URL
    wd.get(url)
    wd.wait(1.5)
    return BeautifulSoup(wd.html, "html.parser")  # 返回解析后的页面内容

def get_any_tab(href):
    any_tab_url = URL_ROOT + href
    wd.get(any_tab_url)
    time.sleep(4)
    soup = BeautifulSoup(wd.html, "html.parser")
    return any_tab_url, soup
def process_row(tr, dateed):
    """
    处理表格中的每一行数据，包括检查日期、查询数据库、处理附件、写入Excel和插入数据库。

    :param tr: 表格行元素
    :param dateed: 日期截止点
    :return: 如果成功处理返回True，否则返回False
    """

    href = tr.find('a').get('href')  # 获取链接
    title = tr.find('a').get('title')  # 获取标题
    dateop = intDate(tr.find_all('td')[3].text)  # 获取发布日期
    datashishi = intDate(tr.find_all('td')[4].text)  # 获取实施日期
    _log.info(f"[{title}]处理中")
    # 如果发布日期早于截止日期，跳过该行
    if dateop <= dateed:
        _log.info("发布日期早于截止日期，跳过该行")
        _log.info("====" * 20)
        return False
    # 查询数据库，检查是否存在相同标题的记录
    sesql = "SELECT * FROM {} WHERE [标题] LIKE '{}'".format(DATABASE_TABLE,title + '%' if title[-3:] == "..." else title)
    if selectsql(sesql):
        _log.info('数据库已存在该数据!')
        _log.info("====" * 20)
        return False

    any_tab_url, soup = get_any_tab(href)
    fujian = []  # 用于存储附件链接
    for test in soup.find_all('a', href=re.compile(r'.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz)+$')):
        ysrc = test.get('href')
        # 构建完整的附件链接
        href_full = any_tab_url.rsplit('/', 1)[0] + "/" + ysrc
        ysrc_name = ysrc.split('/')[-1]  # 获取附件文件名

        # 下载附件
        public_down(href_full, DOWNLOAD_PATH + ysrc_name)
        test['href'] = '/datafolder/卫生健康依法行政法律资源应用支持系统/' + CATEGORY + '/' + ysrc_name  # 更新链接为相对路径
        fujian.append(test['href'])

    if fujian:
        fujian_str = str(fujian).replace("'", '"')  # 将附件列表转换为JSON格式字符串
        wybz = "wjj" + gettimestr() + str(random.randint(0, 9))  # 生成唯一标志
        in_sql = "INSERT INTO {} ([标题], [类别], [发布日期], [实施日期], [全文], [url], [附件], [唯一标志]) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            DATABASE_TABLE, title, CATEGORY, dateop, datashishi, '', href_full, fujian_str, wybz)
        insertsql(in_sql)  # 插入数据库
        data_dt = {
            "标题": title,
            "类别": CATEGORY,
            "发布日期": dateop,
            "实施日期": datashishi,
            "全文": '',
            "url": href_full,
            "附件": fujian_str,
            "唯一标志": wybz
        }
        _log.info("====" * 20)
        return data_dt
    return False


def main():
    """
    主函数，负责组织整个流程，包括初始化Excel文件、遍历页面、处理每一行数据以及发送通知。
    """
    data_lt = []
    timem = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))  # 生成时间戳
    try:
        for page_index in range(1):  # 遍历前10页
            _log.info(f"处理第[{page_index}]页")
            soup = fetch_page_content(page_index)
            for tr in soup.find_all('tr', bgcolor="#ffffff"):  # 遍历每一页中的所有行
                data_dt = process_row(tr, DATE_CUTOFF)
                if data_dt:
                    data_lt.append(data_dt)
            _log.info("====" * 20)
        data_df = pd.DataFrame(data_lt)
        if not data_df.empty:
            file_path = EXCEL_SAVE_PATH.format(timem)
            data_df.to_excel(file_path, index=False)
    except Exception as e:
        print(e)
        _log.error(e)
    finally:
        wd.quit()  # 关闭浏览器


if __name__ == '__main__':
    main()  # 执行主函数
