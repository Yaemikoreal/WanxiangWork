import datetime
import os
import random
import time
from DrissionPage import ChromiumPage, ChromiumOptions
import json
from ProcessingMethod.LoggerSet import logger

co = ChromiumOptions().set_paths()
# 1、设置无头模式：
co.headless(True)
# 2、设置无痕模式：co.incognito(True)
# 3、设置访客模式：co.set_argument('--guest')
# 4、设置请求头user-agent：co.set_user_agent()
# 5、设置指定端口号：co.set_local_port(7890)
# 6、设置代理：co.set_proxy('http://localhost:1080')
page = ChromiumPage(co)


def logining():
    # 访问网站
    url = "http://520mybook.com/account/Login"
    page.get(url)
    time.sleep(random.uniform(0, 3))

    # 输入用户名和密码
    username = "falv1"
    password = "fl123456"

    # 输入
    page.ele('xpath://input[@id="login_username"]').input(username)
    time.sleep(random.uniform(0, 1))
    page.ele('xpath://input[@name="Password"]').input(password)
    time.sleep(random.uniform(0, 1))

    # 点击登录
    page.ele('xpath://button[@class="btn btn-block btn-success btn_login"]').click()
    time.sleep(random.uniform(0, 1))

    # 点击法律数据库
    page.ele('xpath://a[@href="/db/category/3"]').click()
    time.sleep(random.uniform(0, 1))

    # 点击 法宝
    page.ele('xpath://a[@href="/db/entrance/?catId=167"]').click()
    time.sleep(random.uniform(0, 1))

    # 点击指定元素
    page.ele('xpath://div[@class="quick-actions_homepage"]//a[text()="(4)  ZC入口"]').click()
    logger.info("正在等待法宝页面加载完毕(这个过程大概需要15-20秒)!!!")
    # 切换到最新标签页
    tab = page.latest_tab
    time.sleep(random.uniform(15, 20))
    return tab


def get_cookie(tab):
    while True:
        # 刷新
        logger.info("刷新一次")
        tab.refresh()
        time.sleep(3)
        # 获取浏览器cookies并存至文本中
        cookies = tab.cookies()
        if cookies:
            return cookies


def calculate():
    tab = logining()
    cookie = get_cookie(tab)
    x_vpn_token_str = ''
    refresh_str = ''
    # 关闭浏览器
    page.quit()
    logger.info("浏览器已关闭!!")
    for it in cookie:
        name = it.get('name')
        if name == 'refresh':
            refresh = it.get('value')
            refresh_str = f"refresh={refresh}"
        if name == 'x_vpn_token':
            x_vpn_token = it.get('value')
            x_vpn_token_str = f"x_vpn_token={x_vpn_token};"
    cookie_str = f"{x_vpn_token_str}{refresh_str}"

    # 获取脚本所在的绝对路径
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # 构建目标目录的相对路径
    config_directory = os.path.join(script_directory, 'ConfigFile')

    # 确保 ConfigFile 目录存在
    if not os.path.exists(config_directory):
        os.makedirs(config_directory)

    # 构建文件的绝对路径
    file_path = os.path.join(config_directory, 'cookie.txt')

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(cookie_str))
    logger.info("token获取完毕！！！")


if __name__ == '__main__':
    calculate()
