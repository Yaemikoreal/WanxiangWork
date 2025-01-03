import datetime
import os
import random
import time
from DrissionPage import ChromiumPage, ChromiumOptions
import json
from ProcessingMethod.LoggerSet import logger

time.sleep(2)
co = ChromiumOptions().set_paths()
# 设置无头模式
co.headless(True)
page = ChromiumPage(co)


def logining():

    # 访问网站
    url = "http://llb.hggfdd.top/e/action/ListInfo/?classid=73"
    page.get(url)
    time.sleep(random.uniform(0, 3))
    try:
        # 输入用户名和密码
        username = "804324169"
        password = "747641"

        # 输入
        page.ele('css:input[name="username"]').input(username)
        time.sleep(random.uniform(0, 1))
        page.ele('css:input[name="password"]').input(password)
        time.sleep(random.uniform(0, 1))

        # 点击登录
        page.ele('css:input[id="ok2"]').click()
        time.sleep(random.uniform(5, 7))
    finally:
        time.sleep(random.uniform(2, 3))
        page.ele(
            'css:a[href="/e/rk/zhuangchu.php?zhongwenaddid=45333&zhongwenid=512&bclassid=64&userid=449217"]').click()
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
    print("现在的入口是'北大法宝 hazsf'!")
    tab = logining()
    cookie = get_cookie(tab)
    cookie_str = ""
    # 关闭浏览器
    page.quit()
    logger.info("浏览器已关闭!!")
    for it in cookie:
        name = it.get('name')
        value = it.get('value')
        cookie_str += f"{name}={value};"

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
