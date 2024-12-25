import random
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions
from 附件下载程序 import public_down
from 预处理 import _remove_attrs, selectsql, insertsql, intDate, gettimestr
from botpy import logging as botpy_logging

# 设置日志记录
_log = botpy_logging.get_logger()

# 定义常量
CATEGORY = '国家卫生健康委员会各司文件'
BASE_URL = 'http://www.nhc.gov.cn/cms-search/xxgk/searchList.htm?type=search'
URL_CS = 'http://www.nhc.gov.cn/cms-search/xxgk/'
URL_CSN = 'http://www.nhc.gov.cn'
DATE_CUTOFF = 20200701
DOWNLOAD_PATH = r'E:/JXdata/生态环境依法行政法律资源应用支持系统/卫生健康依法行政法律资源应用支持系统/{}/'.format(
    CATEGORY)  # 附件下载路径
EXCEL_SAVE_PATH = r'E:/JXdata/专版系统更新标准收录/收录数据/卫生健康各司文件_{}.xlsx'  # Excel文件保存路径

# 创建浏览器对象并设置选项
options = ChromiumOptions()
options.headless = False  # 设置无头模式
browser = ChromiumPage(options)


def fetch_page_content(url):
    """获取页面内容并返回解析后的 BeautifulSoup 对象"""
    browser.get(url)
    time.sleep(3)
    return BeautifulSoup(browser.html, "html.parser")


def extract_li_elements(soup):
    """从页面中提取所有的 li 元素"""
    ul = soup.find('ul', class_='wgblist')
    return ul.find_all('li', style='height:36px;line-height:36px;')


def process_li_element(li):
    """处理单个 li 元素，提取数据并保存到 Excel 和数据库"""
    a_tag = li.find('a')
    title = a_tag.get('title')
    _log.info(f"处理 标题:[{title}]")
    if '的通知' not in title:
        _log.info("标题不包含【的通知】，跳过")
        _log.info("====" * 20)
        return False

    href = URL_CS + a_tag.get('href')
    date_published = intDate(li.find('div', class_="xxgktime").text)

    # 如果发布日期早于截止日期，跳过该记录
    if date_published <= DATE_CUTOFF:
        _log.info("发布日期早于截止日期，跳过该记录")
        _log.info("====" * 20)
        return False

    # 检查数据库中是否已存在相同标题的记录
    if title.endswith("..."):
        sql_query = f"SELECT * FROM [dbo].[wj-卫计局] WHERE [标题] LIKE '{title[:-3]}%'"
    else:
        sql_query = f"SELECT * FROM [dbo].[wj-卫计局] WHERE [标题] = '{title}'"

    if selectsql(sql_query):
        _log.info(f'当前标题已存在: {title}')
        _log.info("====" * 20)
        return False

    # 访问详情页面，提取详细信息
    browser.get(href)
    time.sleep(3)
    detail_soup = BeautifulSoup(browser.html, "html.parser")
    td_tags = detail_soup.find_all('td')
    publish_dept = td_tags[9].text
    date_published = intDate(td_tags[11].text)
    formatted_date = f"{str(date_published)[:4]}.{str(date_published)[4:6]}.{str(date_published)[6:8]}"
    doc_number = td_tags[7].text
    content_div = detail_soup.find('div', class_='con_font')
    content_div = _remove_attrs(content_div)
    [s.extract() for s in content_div('div', class_="fx fr")]

    attachments = []
    for a in content_div.find_all('a',
                                  href=re.compile(r'.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz)+$')):
        file_url = href + '/../' + a.get('href') if not a.get('href').startswith('/') else URL_CSN + a.get('href')
        file_name = a.get('href').split('/')[-1]
        public_down(file_url, DOWNLOAD_PATH + file_name)
        a['href'] = f'/datafolder/卫生健康依法行政法律资源应用支持系统/{CATEGORY}/{file_name}'
        attachments.append(a['href'])

    for img in content_div.find_all('img'):
        img_url = href + '/../' + img.get('src') if not img.get('src').startswith('/') else URL_CSN + img.get('src')
        img_name = img.get('src').split('/')[-1]
        public_down(img_url, DOWNLOAD_PATH + img_name)
        attachments.append(f'/datafolder/卫生健康依法行政法律资源应用支持系统/{CATEGORY}/{img_name}')
        img['src'] = f'/datafolder/卫生健康依法行政法律资源应用支持系统/{CATEGORY}/{img_name}'

    if not attachments and len(content_div.text) < 100:
        _log.info("该文章没有附件或者文章过于短，跳过")
        _log.info("====" * 20)
        return False

    # 插入数据库
    unique_id = f"wjj{gettimestr()}{random.randint(0, 9)}"
    attachments_str = str(attachments).replace("'", '"')
    insert_sql = f"INSERT INTO [自收录数据].[dbo].[wj-卫计局] ([标题], [类别], [发布部门], [发文字号], [发布日期], [全文], [url], [附件], [唯一标志]) VALUES ('{title}', '{CATEGORY}', '{publish_dept}', '{doc_number}', '{formatted_date}', '{str(content_div)}', '{href}', '{attachments_str}', '{unique_id}')"
    insertsql(insert_sql)
    _log.info(f"插入数据库: {insert_sql}")
    data_dict = {
        "标题": title,
        "类别": CATEGORY,
        "发布部门": publish_dept,
        "发文字号": doc_number,
        "发布日期": formatted_date,
        "实施日期": formatted_date,
        "全文": str(content_div),
        "url": href,
        "附件": attachments_str,
        "唯一标志": unique_id
    }
    _log.info("====" * 20)
    return data_dict


def main():
    """主函数，负责组织整个流程，包括初始化、遍历页面、处理每一行数据以及发送通知"""
    try:
        data_list = []
        lis = []
        timem = time.strftime('%Y%m%d', time.localtime(time.time()))

        # 点击分页按钮，获取更多内容
        for page in range(10):
            if page == 0:
                # 获取第一页内容
                soup = fetch_page_content(BASE_URL)
                lis.extend(extract_li_elements(soup))
            else:
                button = browser.ele('@text():下一页')
                button.click()
                browser.wait(1.5)
                soup = BeautifulSoup(browser.html, "html.parser")
                lis.extend(extract_li_elements(soup))

        # 处理所有 li 元素
        for li in lis:
            data_dict = process_li_element(li)
            if data_dict:
                data_list.append(data_dict)

        if data_list:
            data_df = pd.DataFrame(data_list)
            file_path = EXCEL_SAVE_PATH.format(timem)
            data_df.to_excel(file_path, index=False)
            _log.info(f"文件已经写入到[{file_path}]")
    except Exception as e:
        _log.error(f"发生错误: {e}")
    finally:
        browser.quit()


if __name__ == '__main__':
    main()
