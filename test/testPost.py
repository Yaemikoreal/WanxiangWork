import requests
from bs4 import BeautifulSoup, NavigableString
url = 'http://sjt.gxzf.gov.cn/zwgk/fdzdgknr/zcfg/sjtwj/qtwj/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content,"html.parser")
print(response.status_code)
print(response.json())