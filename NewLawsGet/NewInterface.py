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


def processor(soup, csslist):
    """
    处理 HTML，移除不需要的元素如注释、按钮等，并根据 CSS 列表修改页面结构。

    参数:
    soup (BeautifulSoup): 解析后的 HTML 页面对象。
    csslist (list): 包含选择器和样式的列表。

    返回:
    BeautifulSoup: 修改后的页面对象。
    """
    pp4 = re.compile(r'(display:inline|display: inline)')

    # 移除 HTML 注释和按钮
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for button in soup.find_all('button'):
        button.decompose()

    # 根据提供的 CSS 列表处理页面元素
    for selector, style in csslist:
        if selector.strip() == '':
            continue
        elements = soup.select(selector)
        for element in elements:
            if element.has_attr('style') and pp4.search(element['style']):
                continue
            element.decompose()

    return soup


def ycfirefox():
    """
    配置并启动 Firefox 浏览器，设置无头模式并应用代理。

    返回:
    WebDriver: Selenium WebDriver 对象。
    """
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41"

    firefox_options = Options()
    firefox_options.set_preference('permissions.default.image', 2)  # 禁用图片加载
    firefox_options.set_preference('permissions.default.stylesheet', 2)  # 禁用样式加载

    profile = FirefoxProfile()
    profile.set_preference('network.proxy.type', 1)  # 启用代理
    profile.set_preference('network.proxy.http', '127.0.0.1')
    profile.set_preference('network.proxy.http_port', 1080)
    profile.set_preference('network.proxy.ssl', '127.0.0.1')
    profile.set_preference('network.proxy.ssl_port', 1080)

    driver = webdriver.Firefox(options=firefox_options)
    return driver


def csslists(css_text):
    """
    从 CSS 文本中提取选择器和对应的样式。

    参数:
    css_text (str): CSS 文本。

    返回:
    list: 包含选择器和样式的列表。
    """
    css_patterns = re.compile(r'(.+?)\s*\{(.+?)\}')
    return [(key.strip(), value.strip()) for key, value in css_patterns.findall(css_text)]


def csslisthq(url_base):
    """
    访问基础 URL，获取页面上的所有 CSS 链接，并从中提取 CSS 规则。

    参数:
    url_base (str): 基础 URL 地址。

    返回:
    list: 包含 CSS 选择器和样式的列表。
    """
    driver = ycfirefox()
    driver.get(url_base)
    time.sleep(5)  # 等待页面加载完成
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


@app.route('/htmlqx', methods=['POST'])
def html_cleaner():
    """
    Flask 路由处理器，接收 POST 请求，处理 HTML 并返回修改后的 HTML。

    返回:
    dict: 包含处理后的 HTML 和消息码。
    """
    data = request.form
    html_content = data.get('html', data.get('\ufeffhtml'))

    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        processed_soup = processor(soup, new_css_list)
        return {'html': str(processed_soup), 'msg_code': 0}
    else:
        return {'error': 'No HTML provided', 'msg_code': 1}


if __name__ == '__main__':
    url_base = "https://www.pkulaw.com"
    new_css_list = csslisthq(url_base)  # 在启动时获取 CSS 列表
    app.run(port=8186, debug=False, host='0.0.0.0')
