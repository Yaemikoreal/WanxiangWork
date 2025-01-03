"""
时效性检查自动化
"""
import pandas as pd
import requests
from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import random

co = ChromiumOptions().set_paths()
# 1、设置无头模式：
co.headless(False)
# 2、设置无痕模式：co.incognito(True)
# 3、设置访客模式：co.set_argument('--guest')
# 4、设置请求头user-agent：
co.ignore_certificate_errors(False)
co.set_user_agent(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
# 5、设置指定端口号：co.set_local_port(7890)
# 6、设置代理：co.set_proxy('http://localhost:1080')
page = ChromiumPage(co)


def logining():
    # 访问网站
    url = "http://47.97.3.24:8076/#/historicalRecords"
    page.get(url)
    time.sleep(random.uniform(1, 3))

    # 输入用户名和密码
    username = "cd_jx4218"
    password = "123456"

    # 定位用户名输入框
    username_input = page.ele('xpath://input[@class="el-input__inner" and @name="username"]')
    username_input.input(username)
    time.sleep(random.uniform(0, 1))

    # 定位密码输入框
    password_input = page.ele('css:input.el-input__inner[name="password"]')
    password_input.input(password)
    time.sleep(random.uniform(0, 1))

    # 点击登录
    login_button = page.ele('css:button.el-button.el-button--primary[data-v-29446dc2]')
    login_button.click()
    time.sleep(random.uniform(3, 5))


def click_history():
    # 定位“历史数据”元素
    a_history = page.ele('css:a[href="#/historicalRecords"]')

    # 如果找到了元素，则获取对应的DOM元素
    if a_history:
        # 直接使用DrissionPage的方法点击元素
        a_history.click()
    time.sleep(random.uniform(2, 2.5))
    # 定位“下拉箭头”元素
    xiala = page.ele('css:input[class="el-input__inner"]')

    # 点击下拉箭头
    if xiala:
        xiala.click()
        print("点击了下拉箭头")
    else:
        print("未找到下拉箭头元素")
    # 等待下拉菜单加载
    time.sleep(random.uniform(2, 2.5))

    # 定位“地方法规”元素
    dropdown_items = page.eles('css:li[class="el-select-dropdown__item"]')
    if dropdown_items:
        for it in dropdown_items:
            if it.raw_text == "地方法规":
                it.click()
                print("点击了地方法规")


def select_data(title):
    """
    查询数据内容
    :param title:
    :return:
    """
    dropdown_items = page.eles('css:input[class="el-input__inner"]')
    for it in dropdown_items:
        placeholder = it.attr('placeholder')
        if placeholder == '请输入标题内容':
            it.input(title, clear=True)
            print(f"已输入标题: [{title}]")
            break
    time.sleep(random.uniform(2, 2.5))
    button_kys = page.eles('css:button[type="button"]')
    for item in button_kys:
        bt_class = item.attr('class')
        if bt_class == 'el-button el-button--primary':
            item.click()
            print("已点击查询!")
            break
    time.sleep(random.uniform(2, 2.5))
    tr_msgs = page.eles('css:tr[class="el-table__row"]')
    for tr in tr_msgs:
        div_msgs = tr.eles('css:div[class="cell el-tooltip"]')
        for div in div_msgs:
            raw_text = div.raw_text
            if raw_text == title:
                button_check = tr.ele('css:button[class="el-button el-tooltip btn-bottom el-button--primary"]')
                button_check.click.multi(3)
                print(f"已点击对应修改: [{raw_text}]")
                time.sleep(random.uniform(2, 2.5))
                break


def update_content(failure_basis):
    bj_msg = page.ele('css:div[aria-label="编辑"]')
    input_msgs = bj_msg.eles('css:div[class="from-box"]')
    input_msgs.reverse()
    for it in input_msgs:
        raw_text = it.raw_text
        if "来源" == raw_text:
            input_yx = it.ele('css:input[class="el-input__inner"]')
            input_yx.click()

        if "失效依据" == raw_text:
            input_yx = it.ele('css:input[class="el-input__inner"]')
            input_yx.click()
            time.sleep(random.uniform(2, 2.5))
            input_yx.input(failure_basis)
            print(f"已经填入失效依据: {failure_basis}")

        if "时效性" in raw_text:
            input_yx = it.ele('css:input[class="el-input__inner"]')
            input_yx.click()
            time.sleep(random.uniform(2, 2.5))
            input_yx.input("失效\n")
            time.sleep(random.uniform(2, 2.5))
            # 打印输入框的值进行验证
            print(f"Input value: {input_yx.value}")
            button_yx = it.ele('css:button[class="el-button el-button--primary"]')
            # 使用JavaScript来模拟点击按钮
            button_yx.click()
            input_yx.click()
            time.sleep(random.uniform(2, 2.5))
            # 点击元素正下方60像素的位置
            input_yx.click.at(offset_y=60)
            print("时效性更换为: '02:失效'")
            print(f"Input value: {input_yx.value}")
            if input_yx.value != '02:失效':
                print(f"小心这条数据的时效性!!!!!!!")
            # try_num = 10
            # while True:
            #     print("获取失效值Ing~")
            #     yx_values = page.eles('css:li[class="el-select-dropdown__item hover"]')
            #     if try_num <= 0:
            #         print(f"小心这条数据的时效性!!!!!!!")
            #         break
            #     if not yx_values:
            #         try_num -= 1
            #         continue
            #     else:
            #         break
            # for yx in yx_values:
            #     if yx.raw_text == '02:失效':
            #         yx.click()
            #         print("时效性更换为: '02:失效'")

    time.sleep(random.uniform(2, 2.5))
    ok_buttons = page.eles('css:button[class="el-button el-button--primary"]')
    for item in ok_buttons:
        raw_text_button = item.raw_text
        if raw_text_button == '确 定':
            item.click()
            print("已经尝试提交修改!")
            break
    error_msgs = page.eles('css:p[class="el-message__content"]')
    for it in error_msgs:
        if it.raw_text == '该数据已存在，唯一标识重复！':
            not_buttons = page.eles('css:button[class="el-button el-button--default"]')
            for item in not_buttons:
                raw_text_button = item.raw_text
                if raw_text_button == '取 消':
                    item.click()
                    print("已经取消修改!")
                    break
    print("===" * 30)
    time.sleep(random.uniform(4,8))


def read_excel():
    # 指定Excel文件路径
    file_path = r'E:\JXdata\每月手动数据检查\排查_jx_后.xlsx'
    # 读取Excel文件的第一个工作表，并存储为DataFrame
    data_df = pd.read_excel(file_path)
    data_df = data_df[data_df["标记"] == '需要查看']
    # data_df = data_df.head(6)
    return data_df


def calculate_row(row):
    title = row.get('法器废止文件')
    yiju = row.get('失效依据')
    print(f"正在处理: [{title}]")
    try_num = 2
    while try_num > 0:
        try:
            click_history()
            select_data(str(title))
            update_content(str(yiju))
            break
        except Exception as e:
            try_num -= 1
            print(f"处理{title}出错:{e}")
            time.sleep(5)
    time.sleep(random.uniform(8, 11))


def calculate():
    data_df = read_excel()
    logining()
    data_df.apply(calculate_row, axis=1)


if __name__ == '__main__':
    calculate()
