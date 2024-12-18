import random
import time
from AuditOffice import main as audit_calculate
from query import PublicFunction as pf

"""
该脚本用于获取云南省审计厅的文件
"""


class TotalProcessAudit:
    def __init__(self):
        self.center_url = 'http://audit.yn.gov.cn'
        self.url_categories = {
            "通知通告": "http://audit.yn.gov.cn/html/zhengfuxinxigongkai/fadingzhudonggongkaineirong/tongzhitonggao/",
            "行政处罚": "http://audit.yn.gov.cn/html/zhengfuxinxigongkai/fadingzhudonggongkaineirong/xingzhengchufa/",
            "政策解读": "http://audit.yn.gov.cn/html/zhengfuxinxigongkai/fadingzhudonggongkaineirong/zhengcejiedu/",
            "规范性文件": "http://audit.yn.gov.cn/html/zhengfuxinxigongkai/zhengcewenjian/xingzhengguifanxingwenjian/",
            "其他文件": "http://audit.yn.gov.cn/html/zhengfuxinxigongkai/zhengcewenjian/qitawenjian/",
            "建议提案办理": "http://audit.yn.gov.cn/html/zhengfuxinxigongkai/fadingzhudonggongkaineirong/jianyitianbanli/",
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

    def get_title_urls(self, base_url):
        data_lt = []
        soup = pf.fetch_url(base_url, self.headers)
        title_soup = soup.find(["div", "td"], attrs={"class": ["scroll_wrap", "tcc"]})
        a_tags = title_soup.find_all('a', href=True)
        for tag in a_tags:
            title_text = tag.get_text()
            url_text = tag.get('href').replace('./', '')
            url_text = self.center_url + url_text
            data_dt = {
                "标题": title_text,
                "来源": url_text
            }
            data_lt.append(data_dt)
        return data_lt

    #TODO

    def process_category(self, category, base_url):
        print(f"正在收录 [{category}]")
        print("====" * 20)
        title_urls = self.get_title_urls(base_url)
        data = {
            "start_url": base_url,
            "lasy_department": '云南省审计厅',
            "category": category,
            "title_url_lt": title_urls
        }
        audit_calculate(data)
        print("====" * 20)

    def total_process(self):
        for category, url in self.url_categories.items():
            self.process_category(category, url)
            time.sleep(random.uniform(2, 2.5))


if __name__ == '__main__':
    obj = TotalProcessAudit()
    obj.total_process()
