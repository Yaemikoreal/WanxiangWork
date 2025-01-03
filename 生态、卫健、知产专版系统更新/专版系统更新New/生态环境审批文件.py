import random
import re
import time
import requests
from bs4 import BeautifulSoup
from 预处理 import _remove_attrs, intaa, insertsql, selectsql, gettimestr
from 附件下载程序 import public_down


def download_attachment(href, base_url, title, fujian, category):
    if 'http' in href:
        full_url = href
    else:
        href_parts = base_url.split('/')
        ysrc = href[2:]
        full_url = f"{href_parts[0]}//{href_parts[2]}/{href_parts[3]}/{href_parts[4]}/{href_parts[5]}/{href_parts[6]}/{ysrc}"

    print(full_url)
    download_path = f'./生态环境依法行政法律资源应用支持系统/{category}/' + ysrc
    public_down(full_url, download_path)
    relative_path = f'/datafolder/生态环境依法行政法律资源应用支持系统/{category}/' + ysrc
    fujian.append(relative_path)
    return relative_path


def process_li_element(li, url, dateed, category):
    dateop = intaa(li.find('span').text)
    if dateop <= dateed:
        return False

    title = li.find('a').text.strip()
    if title.endswith("..."):
        title = title[:-3]
        sesql = f"SELECT * FROM [dbo].[hb-环保局] WHERE [标题] LIKE '{title}%'"
    else:
        sesql = f"SELECT * FROM [dbo].[hb-环保局] WHERE [标题] = '{title}'"

    if selectsql(sesql) or title == '关于批准大连宝原核设备有限公司变更一类放射性物品运输容器制造许可活动范围的通知':
        return False

    ss = li.find('a')['href']
    fbbm = ""
    fwzh = ""
    dateFb = ""
    fujian = []

    for test in li.find_all('a', href=re.compile(r'.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz)+$')):
        relative_path = download_attachment(test['href'], url, title, fujian, category)
        test['href'] = relative_path

    wybz = f"hbj{gettimestr()}{random.randint(0, 9)}"
    fujian_str = str(fujian).replace("'", '"')

    in_sql = f"""
    INSERT INTO [自收录数据].[dbo].[hb-环保局] 
    ([标题], [类别], [发文字号], [发布部门], [发布日期], [实施日期], [全文], [url], [附件], [唯一标志]) 
    VALUES 
    ('{title}', '{category}', '{fwzh}', '{fbbm}', '{dateFb}', '{dateop}', '<div><a href="{relative_path}">{title}附件</a></div>', '{url}', '{fujian_str}', '{wybz}')
    """
    insertsql(in_sql)
    return True


def scrape_page(url, dateed, category):
    response = requests.get(url)
    response.encoding = "utf-8"
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find('ul', id="div")
    lis = ul.find_all('li') if ul else []
    fujian = []
    for li in lis:
        if not process_li_element(li, url, dateed, category):
            continue

        ss = li.find('a')['href']
        if not ss.startswith('http'):
            ss = url + ss

        rese = requests.get(ss)
        rese.encoding = "utf-8"
        so = BeautifulSoup(rese.text, "html.parser")

        ul = so.find('ul')
        [s.extract() for s in ul.find_all('span')] if ul else None

        div = so.find_all('div')
        if div:
            title = div[0].text.strip()
            fbbm = div[3].text.strip() if len(div) > 3 else ""
            dateFb = div[4].text.strip() if len(div) > 4 else ""
            fwzh = div[5].text.strip() if len(div) > 5 else ""

        box = so.find('div', class_='Custom_UnionStyle') or \
              so.find('div', class_='neiright_JPZ_GK_CP') or \
              so.find('div', class_='content_body_box')

        if box:
            box = _remove_attrs(box)
            for test in box.find_all('a', href=re.compile(r'.html')):
                test.replace_with(BeautifulSoup(f"<p>{test.text}</p>", 'html.parser'))

            for test in box.find_all('a', href=re.compile(
                    r'.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz)+$')):
                download_attachment(test['href'], rese.url, title, fujian, category)

            for img in box.find_all('img'):
                download_attachment(img['src'], rese.url, title, fujian, category)

            strcc = ''.join(str(bb) for bb in box)
            datefb_formatted = time.strftime('%Y.%m.%d', time.strptime(str(dateFb).replace('-', ''), '%Y%m%d'))
            dateop_formatted = time.strftime('%Y.%m.%d', time.strptime(str(dateop), '%Y%m%d'))

            in_sql = f"""
            INSERT INTO [自收录数据].[dbo].[hb-环保局] 
            ([标题], [类别], [发文字号], [发布部门], [发布日期], [实施日期], [全文], [url], [附件], [唯一标志]) 
            VALUES 
            ('{title}', '{category}', '{fwzh}', '{fbbm}', '{datefb_formatted}', '{dateop_formatted}', '<div>{strcc}</div>', '{rese.url}', '{fujian_str}', '{wybz}')
            """
            insertsql(in_sql)


def main():
    category = '生态环境审批文件'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10-12.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    base_url = 'http://www.mee.gov.cn/zcwj/xzspwj/'
    dateed = 20180808

    for cn in range(16):  # 爬取16页
        url = base_url if cn == 0 else f"{base_url}index_{cn}.shtml"
        print(f"第 {cn + 1} 页")
        scrape_page(url, dateed, category)


if __name__ == "__main__":
    main()