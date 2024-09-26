import random
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# 设置 chromedriver 的路径
chromedriver_path = r'E:\JXdata\chromedriver-win64\chromedriver-win64\chromedriver.exe'  # Windows 示例
# 初始化 WebDriver 并设置无头模式
chrome_options = Options()
chrome_options.add_argument('--headless')  # 启用无头模式
chrome_options.add_argument('--disable-gpu')  # 禁用 GPU 加速
chrome_options.add_argument("--no-sandbox")  # 解决DevToolsActivePort文件不存在的报错
chrome_options.add_argument("--window-size=1920x1080")  # 设置窗口大小
# 设置 ChromeDriver 服务
service = Service(executable_path=chromedriver_path)
# 初始化 WebDriver
browser = webdriver.Chrome(service=service, options=chrome_options)


def logining():
    # 访问网站
    url = "http://520mybook.com/account/Login"
    browser.get(url)
    time.sleep(random.uniform(0, 3))

    # 输入用户名和密码
    username = "falv1"
    password = "fl123456"

    # 等待用户名输入框出现
    username_input_id = 'login_username'
    try:
        username_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, username_input_id))
        )
        username_input.send_keys(username)
    except Exception as e:
        print(f"Username 超时或者出错: {e}")
    else:
        print("用户名 输入完毕!!!")

    # 等待密码输入框出现
    password_input_id = 'Password'
    try:
        password_input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.NAME, password_input_id))
        )
        password_input.send_keys(password)
    except Exception as e:
        print(f"Password 超时或者出错: {e}")
    else:
        print("密码 输入完毕!!!")

    # 等待登录按钮出现
    login_button_xpath = '//button[@class="btn btn-block btn-success btn_login"]'
    try:
        login_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        login_button.click()
    except Exception as e:
        print(f"Login button 超时或者出错: {e}")
    else:
        print("登录按钮已经按下!!!")

    # 等待登录完成
    try:
        WebDriverWait(browser, 20).until(
            EC.url_changes(url)
        )
    except Exception as e:
        print(f"Login 超时或者出错: {e}")
    else:
        print("登录成功!!!")

    # 等待“法律数据库”链接出现
    legal_db_link_xpath = '//a[@href="/db/category/3"]'
    try:
        legal_db_link = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, legal_db_link_xpath))
        )
        legal_db_link.click()
    except Exception as e:
        print(f"Legal database 超时或者出错: {e}")
    else:
        print("法律数据库 按钮已点击!!!")

    # 等待“F宝数据库”链接出现
    legal_db_link_xpath = '//a[@href="/db/entrance/?catId=167"]'
    try:
        legal_db_link = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, legal_db_link_xpath))
        )
        legal_db_link.click()
    except Exception as e:
        print(f"F宝数据库 超时或者出错: {e}")
    else:
        print("F宝数据库 按钮已点击!!!")

    time.sleep(random.uniform(0, 2))
    try:
        # 等待指定元素出现
        element = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="quick-actions_homepage"]//a[text()="(4)  ZC入口"]'))
        )
        # 点击元素
        element.click()
    except Exception as e:
        print(f"An error occurred: {e}")
    else:
        print("正在跳转到北大法宝，准备获取token!!!")



if __name__ == '__main__':
    logining()
    # 关闭浏览器
    browser.quit()
