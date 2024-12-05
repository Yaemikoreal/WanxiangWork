from MarketSupervisionAdministration import main as market_calculate
import random
import time
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions
"""
该脚本用于获取江苏省市场监督管理局的文件
"""
co = ChromiumOptions().set_paths()
# 设置无头模式
co.headless(True)
page = ChromiumPage(co)
# 江苏省市场监督管理局
center_url = 'http://scjgj.jiangsu.gov.cn'
url_dt = {"通知公告": "http://scjgj.jiangsu.gov.cn/col/col78963/index.html",
          "规划信息": "http://scjgj.jiangsu.gov.cn/col/col78958/index.html",
          "综合通知": "http://scjgj.jiangsu.gov.cn/col/col78968/index.html",
          "法律法规": "http://scjgj.jiangsu.gov.cn/col/col78977/index.html",
          "政策解读": "http://scjgj.jiangsu.gov.cn/col/col78965/index.html",
          "建议提案办理结果": "http://scjgj.jiangsu.gov.cn/col/col78960/index.html",
          "政策文件": "http://scjgj.jiangsu.gov.cn/col/col78964/index.html",
          }
title_uid_dt = {
    "通知公告": "332979"
}


def get_title_url(title, title_url):
    uid = title_uid_dt.get(title)
    if not uid:
        uid = "310641"
    title_url_lt = []
    for it in range(2):
        try_num = 2
        while try_num > 0:
            try:
                url = title_url + f'?uid={uid}&pageNum={it + 1}'
                page.get(url, retry=2, interval=3, timeout=10)
                time.sleep(random.uniform(3, 5))
                soup = BeautifulSoup(page.html, 'html.parser')
                titles_soup = soup.find_all('a', href=True, title=True, target=True)
                if not titles_soup:
                    try_num -= 1
                    page.refresh()
                    continue
                for tag in titles_soup:
                    full_url = tag.get('href')
                    full_title = tag.get('title')
                    title_url_dt = {
                        "标题": full_title,
                        "来源": center_url + full_url
                    }
                    # print(title_url_dt)
                    title_url_lt.append(title_url_dt)
                break
            except Exception as e:
                print(f"标题和url获取失败:[{e}] url:[{title_url + f'?uid=310641&pageNum={it + 1}'}]")
                time.sleep(random.uniform(1, 2))
                try_num -= 1
    print(f"共有 [{len(title_url_lt)}] 条数据")
    return title_url_lt


def total_process():
    for key, value in url_dt.items():
        print(f"正在收录     [{key}]")
        print("====" * 20)
        title_url_lt = get_title_url(key, value)
        data_dt = {
            "start_url": value,  # 访问路径
            "lasy_department": '江苏省市场监督管理局',  # 在函数返回为空的时候指定发布部门
            "category": "",
            "title_url_lt": title_url_lt
        }
        market_calculate(data_dt)
        print("====" * 20)
    # 关闭浏览器
    page.quit()


if __name__ == '__main__':
    total_process()
