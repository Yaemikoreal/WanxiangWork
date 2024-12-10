from AuditOffice import main as audit_calculate
import random
import time
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage, ChromiumOptions

"""
该脚本用于获取江苏省审计厅的文件
"""
co = ChromiumOptions().set_paths()
# 设置无头模式
co.headless(True)
page = ChromiumPage(co)


class TotalProcessAudit:
    def __init__(self):
        # 江苏省审计厅
        self.center_url = 'https://jssjt.jiangsu.gov.cn'
        self.url_dt = {"政策解读": "https://jssjt.jiangsu.gov.cn/col/col84864/index.html",
                       "规划计划": "https://jssjt.jiangsu.gov.cn/col/col80112/index.html",
                       "审计报告解读": "https://jssjt.jiangsu.gov.cn/col/col80120/index.html",
                       "政策法规": "https://jssjt.jiangsu.gov.cn/col/col80111/index.html",
                       }
        self.title_uid_dt = {
            "通知公告": "332979",
            "政策法规": "424041",
            "政策解读": "424041"
        }
        self.old_soup = None

    def get_title_url(self, title, title_url):
        uid = self.title_uid_dt.get(title)
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
                    title_soup = soup.find('ul', id="gz_list")
                    if title_soup == self.old_soup:
                        break
                    self.old_soup = title_soup
                    titles_soup = title_soup.find_all('a', href=True, title=True, target=True)
                    if not titles_soup:
                        try_num -= 1
                        page.refresh()
                        continue
                    for tag in titles_soup:
                        full_url = tag.get('href')
                        full_title = tag.get('title')
                        title_url_dt = {
                            "标题": full_title,
                            "来源": self.center_url + full_url
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

    def total_process(self):
        for key, value in self.url_dt.items():
            print(f"正在收录     [{key}]")
            print("====" * 20)
            title_url_lt = self.get_title_url(key, value)
            data_dt = {
                "start_url": value,  # 访问路径
                "lasy_department": '江苏省审计厅',  # 在函数返回为空的时候指定发布部门
                "category": "",
                "title_url_lt": title_url_lt
            }
            audit_calculate(data_dt)
            print("====" * 20)
        # 关闭浏览器
        page.quit()


if __name__ == '__main__':
    obj = TotalProcessAudit()
    obj.total_process()
