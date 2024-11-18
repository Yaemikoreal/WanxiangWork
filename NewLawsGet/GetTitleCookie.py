import datetime
import os
import random
import time
from DrissionPage import ChromiumPage, ChromiumOptions
import json
from ProcessingMethod.LoggerSet import logger

co = ChromiumOptions().set_paths()
co.headless(False)
page = ChromiumPage(co).latest_tab


def get_cookies():
    logger.info("开始监听")
    page.listen.start('RecordSearch')  # 开始监听，指定获取包含该文本的数据包
    # 访问网站
    url = "https://www.pkulaw.com/"
    page.get(url)
    time.sleep(random.uniform(4, 5))

    filename = page.ele('css:a[id="RelatedPromptedport_1_a"]')
    filename.click()
    time.sleep(random.uniform(2, 3))
    logger.info("开始获取")
    for packet in page.listen.steps():
        try:
            if packet.method == 'POST' and packet.resourceType == 'XHR':
                requests_msg = packet.request
                new_headers = requests_msg.headers
                return new_headers
        except Exception as e:
            print(e)
    return None


def calculate():
    new_headers = get_cookies()
    if not new_headers:
        return None
    new_headers = dict(new_headers)
    logger.info("new_headers获取完毕！！！")
    return new_headers


if __name__ == '__main__':
    calculate()
