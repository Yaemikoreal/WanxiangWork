import random
import time

import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.spc.org.cn/basicsearch'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'
}


# 接受一个标准号，返回该标准售价
def get_Sell(biaozhunhao):
    data = {
        'text': f'{biaozhunhao}',
        'search': 'a100'
    }
    try_num = 2
    while try_num > 0:
        try:
            resp = requests.post(url, data=data, headers=headers)
            soup = BeautifulSoup(resp.text, 'html.parser')
            info = soup.find('div', class_='search-list').find('p', class_='tubuylist').get_text()
            info = re.findall(r'(\d+)', info)[0]
            return info
        except Exception as e:
            print("价格查询错误，重试~")
            try_num -= 1
            time.sleep(random.uniform(2, 2.5))
    return 0


if __name__ == '__main__':
    while True:
        names = input('输入标准')
        resp = get_Sell(biaozhunhao=names)
