import re
import time
from flask import Flask, request
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import requests
import urllib3

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)


# 处理 HTML 的函数
def processor(soup, csslist):
    pp4 = re.compile(r'(display:inline|display: inline)')

    # 移除注释和按钮
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for button in soup.find_all('button'):
        button.decompose()

    # 处理 CSS 列表
    for selector, style in csslist:
        if selector.strip() == '':
            continue
        elements = soup.select(selector)
        for element in elements:
            if element.has_attr('style') and pp4.search(element['style']):
                continue
            element.decompose()

    return soup


# 配置并启动 Firefox 浏览器
def ycfirefox():
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41"

    firefox_options = Options()
    firefox_options.set_preference('permissions.default.image', 2)
    firefox_options.set_preference('permissions.default.stylesheet', 2)

    profile = FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)
    profile.set_preference('network.proxy.http', '127.0.0.1')
    profile.set_preference('network.proxy.http_port', 1080)
    profile.set_preference('network.proxy.ssl', '127.0.0.1')
    profile.set_preference('network.proxy.ssl_port', 1080)

    driver = webdriver.Firefox(options=firefox_options)
    return driver


# 提取 CSS 列表
def csslists(css_text):
    css_patterns = re.compile(r'(.+?)\s*\{(.+?)\}')
    return [(key.strip(), value.strip()) for key, value in css_patterns.findall(css_text)]


# 获取 CSS 列表
def csslisthq(url_base):
    driver = ycfirefox()
    driver.get(url_base)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    css_links = soup.find_all('link', href=True)

    new_css_list = []
    for link in css_links:
        href = link['href']
        if not href.startswith('http'):
            href = url_base + href
        response = requests.get(href, verify=False)
        new_css_list.extend(csslists(response.text))

    return new_css_list


# Flask 路由处理
@app.route('/htmlqx', methods=['POST'])
def html_cleaner():
    data = request.form
    html_content = data.get('html', data.get('\ufeffhtml'))

    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        processed_soup = processor(soup, new_css_list)
        return {'html': str(processed_soup), 'msg_code': 0}


# 主函数
if __name__ == '__main__':
    url_base = "https://www.pkulaw.com"
    new_css_list = csslisthq(url_base)
    app.run(port=8186, debug=False, host='0.0.0.0')
