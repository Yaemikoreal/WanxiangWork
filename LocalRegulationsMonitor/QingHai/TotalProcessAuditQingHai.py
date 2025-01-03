import random
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from DepartmentTransportation import main as audit_calculate
from query import PublicFunction as pf
from ScienceDepartment import main as calculate_science

"""
该脚本用于获取青海省交通运输厅,青海省科技厅的文件
"""
# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


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
        return any(item.get("来源") == new_value for item in data)

    def get_title_urls(self, base_url, bm):
        data_lt = []
        try:
            soup = pf.fetch_url(base_url, self.headers)
            title_soup = soup.find(["ul", "div"], attrs={
                "class": ["xxgkList", "gz", "list_ul", "NewXXGK_Content_Right_Main NoPadding"]})
            if not title_soup:
                logging.warning(f"未能找到标题列表: {base_url}")
                return data_lt

            a_tags = title_soup.find_all('a', href=True, target="_blank")
            for tag in a_tags:
                title_text = tag.get_text(strip=True)
                url_text = tag.get('href').replace('./', '')
                if "www." not in url_text:
                    url_text = self.center_url.get(bm) + url_text

                data_dt = {
                    "标题": title_text,
                    "来源": url_text
                }
                if not self.check_source_exists(data_lt, url_text):
                    data_lt.append(data_dt)
        except Exception as e:
            logging.error(f"获取标题和URL时发生错误: {base_url}, 错误: {e}")

        return data_lt

    def process_category(self, category, base_url, bm):
        logging.info(f"正在收录 [{category}]")
        logging.info("====" * 20)
        title_urls = self.get_title_urls(base_url, bm)
        data = {
            "start_url": base_url,
            "last_department": bm,
            "category": category,
            "title_url_lt": title_urls
        }
        try:
            if bm == "青海省交通运输厅":
                audit_calculate(data)
            elif bm in ["青海省科学技术厅", "青海省广播电视局"]:
                calculate_science(data)
        except Exception as e:
            logging.error(f"处理分类 [{category}] 时发生错误: {e}")

        logging.info("====" * 20)

    def total_process(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = []
            for bm, urls in self.url_categories.items():
                for category, url in urls.items():
                    futures.append(executor.submit(self.process_category, category, url, bm))
                    time.sleep(random.uniform(2, 2.5))  # 确保每个请求之间有足够的间隔

            # 等待所有任务完成
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"任务执行时发生错误: {e}")


if __name__ == '__main__':
    obj = TotalProcessAudit()
    obj.total_process()
