import random
import time
from DepartmentTransportation import main as audit_calculate
from query import PublicFunction as pf
from ScienceDepartment import main as calculate_science

"""
该脚本用于获取青海省交通运输厅,青海省科技厅的文件
"""


class TotalProcessAudit:
    def __init__(self):
        self.center_url = {
            "青海省交通运输厅": 'https://jtyst.qinghai.gov.cn',
            "青海省科学技术厅": 'https://kjt.qinghai.gov.cn',
            "青海省广播电视局": 'http://gdj.qinghai.gov.cn'
        }
        self.url_categories = {
            "青海省交通运输厅": {
                "部门规章": "https://jtyst.qinghai.gov.cn/jtyst/zwgk/zfxxgkml/gfxwj/gz/index.html",
                "其他文件": "https://jtyst.qinghai.gov.cn/jtyst/zwgk/zfxxgkml/zcfg/qtwj/443fd9cf-1.html",
                "政策解读": "https://jtyst.qinghai.gov.cn/jtyst/zwgk/zfxxgkml/zcfg/zcjd/bjzcjd/index.html",
                "政协提案": "https://jtyst.qinghai.gov.cn/jtyst/zwgk/zfxxgkml/rdjyzxta/zxta/index.html"
            },
            "青海省科学技术厅": {
                "提案办理": "https://kjt.qinghai.gov.cn/content/view/cate_id/79/page/",
                "政策解读": "https://kjt.qinghai.gov.cn/content/view/cate_id/9/page/",
                "依法行政": "https://kjt.qinghai.gov.cn/content/view/cate_id/88/page/"
            },
            "青海省广播电视局": {
                "政策解读": "http://gdj.qinghai.gov.cn/channel/5dd625f91e8299f68516e57c?p=1",
                "政策法规": "http://gdj.qinghai.gov.cn/channel/5dd625f11e8299f68516e57b?p=1"
            }

        }
        self.title_uids = {
            "通知公告": "332979",
            "政策法规": "424041",
            "政策解读": "424041"
        }
        self.default_uid = "310641"
        self.page = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }

    def check_source_exists(self, data, new_value):
        for item in data:
            if item.get("来源") == new_value:
                return True
        return False

    def get_title_urls(self, base_url, bm):
        data_lt = []
        soup = pf.fetch_url(base_url, self.headers)
        title_soup = soup.find(["ul", "div"], attrs={"class": ["xxgkList", "gz", "list_ul","NewXXGK_Content_Right_Main NoPadding"]})
        a_tags = title_soup.find_all('a', href=True, target="_blank")
        for tag in a_tags:
            title_text = tag.get_text()
            url_text = tag.get('href').replace('./', '')
            if "www." not in url_text:
                url_text = self.center_url.get(bm) + url_text
            data_dt = {
                "标题": title_text,
                "来源": url_text
            }
            if not self.check_source_exists(data_lt, url_text):
                data_lt.append(data_dt)
        return data_lt

    def process_category(self, category, base_url, bm):
        print(f"正在收录 [{category}]")
        print("====" * 20)
        title_urls = self.get_title_urls(base_url, bm)
        data = {
            "start_url": base_url,
            "lasy_department": bm,
            "category": "",
            "title_url_lt": title_urls
        }
        if bm == "青海省交通运输厅":
            audit_calculate(data)
        elif bm == "青海省科学技术厅":
            calculate_science(data)
        elif bm == "青海省广播电视局":
            calculate_science(data)
        print("====" * 20)

    def total_process(self):
        for bm, urls in self.url_categories.items():
            if bm == "青海省交通运输厅":
                for category, url in urls.items():
                    self.process_category(category, url, bm)
                    time.sleep(random.uniform(2, 2.5))
            if bm == "青海省科学技术厅":
                for category, url in urls.items():
                    self.process_category(category, url, bm)
                    time.sleep(random.uniform(2, 2.5))
            if bm == "青海省广播电视局":
                for category, url in urls.items():
                    self.process_category(category, url, bm)
                    time.sleep(random.uniform(2, 2.5))


if __name__ == '__main__':
    obj = TotalProcessAudit()
    obj.total_process()
