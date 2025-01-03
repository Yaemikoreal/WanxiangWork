import datetime
import os
import random
import time

import requests
from DrissionPage import ChromiumPage, ChromiumOptions
import json

co = ChromiumOptions().set_paths()

# 1、设置无头模式：
co.headless(False)
# # 2、设置无痕模式：
# co.incognito(True)
# # 3、设置访客模式：
# co.set_argument('--guest')

user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
# 4、设置请求头
co.set_user_agent(user_agent)
# 5、设置指定端口号：co.set_local_port(7890)
page = ChromiumPage(co)


def logining():
    # 访问网站
    url = "https://www.pkulaw.com/advanced/law/chl"
    page.get(url)

    page.listen.start(targets="/list/chl", method='POST')  # 开始监听，指定获取包含该文本的数据包(部分url)
    print("获取ing")
    stop_num = 5
    while True:
        time.sleep(random.uniform(0, 2))
        print("获取心跳~")
        page.refresh()
        time.sleep(3)
        # 等待并获取一个数据包
        res = page.listen.wait(timeout=5)
        if not res:
            stop_num -= 1
            continue
        authorization_headers = res.request.headers
        authorization = authorization_headers.get("Authorization")
        if not authorization:
            print(f"本次未获取到authorization")
            stop_num -= 1
            continue
        if "Bearer" in authorization:
            print(f"获取到authorization: [{authorization}]")
            return authorization
        if stop_num == 0:
            print("未能获取到authorization验证码值")
            break
        stop_num -= 1


def calculate():
    authorization = logining()
    # 关闭浏览器
    page.quit()
    # 获取脚本所在的绝对路径
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # 获取脚本所在目录的父目录的绝对路径
    parent_directory = os.path.dirname(script_directory)

    # 构建目标目录的相对路径
    config_directory = os.path.join(parent_directory, 'ConfigFile')

    # 确保 ConfigFile 目录存在
    if not os.path.exists(config_directory):
        os.makedirs(config_directory)

    # 构建文件的绝对路径
    file_path = os.path.join(config_directory, 'authorization.txt')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(authorization))
        print("authorization获取完毕！！！")


if __name__ == '__main__':
    calculate()
