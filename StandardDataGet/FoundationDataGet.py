import pandas as pd
from DrissionPage import ChromiumPage, ChromiumOptions
from bs4 import BeautifulSoup
import time
import random

co = ChromiumOptions().set_paths()
co.headless(True)
co.ignore_certificate_errors(False)
co.set_user_agent(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
page = ChromiumPage(co)
"""
该方法用于获取标准信息的url链接并储存到excel
"""


class FoundationData:
    def __init__(self):
        self.url = "https://www.spc.org.cn/basicsearch"
        self.folder_path = r'tools/标准号1.xlsx'
        self.read_df = pd.read_excel(self.folder_path)

    def get_data(self, page, filename, filecode):
        try_num = 3
        while try_num > 0:
            try:
                time.sleep(random.uniform(2, 3))
                filecode_input = page.ele('css:input[class="ky"]', timeout=10)
                filecode_input.input(filecode, clear=True)
                time.sleep(random.uniform(0, 2))
                search_button = page.ele('css:input.btn[value="检索"]', timeout=10)
                search_button.click()

                time.sleep(1)
                html_content = page.html
                soup = BeautifulSoup(html_content, 'html.parser')
                msg_soup = soup.find('div', attrs={'class': "titleft"})
                if msg_soup:
                    msg_all = msg_soup.find('a', href=True, style=True)
                    href_any = msg_all['href']
                    data_dt = {
                        "标题": filename,
                        "链接": 'https://www.spc.org.cn' + href_any
                    }
                    print(data_dt)
                    print("====" * 30)
                    return data_dt, True
                else:
                    print(f"【{filename}】 获取失败!!!")
                    print("====" * 30)
                    return {filename: ''}, False
            except Exception as e:
                print(f"错误:{e},重试~")
                try_num -= 1
                page.get(self.url)
                time.sleep(3)

    def visit_real(self):
        data_lt = []
        not_data_lt = []
        # 访问网站
        page.get(self.url)
        time.sleep(random.uniform(2, 4))
        for index, row in self.read_df.iterrows():
            filename = row.get('Name')
            filecode = row.get('Code')
            print(f"处理{filename}")
            data_dt, get_status = self.get_data(page, filename, filecode)
            if get_status and data_dt:
                data_lt.append(data_dt)
            else:
                not_data_lt.append(data_dt)

        data_df = pd.DataFrame(data_lt)
        with pd.ExcelWriter(rf"tools/标准号1_urls.xlsx") as writer:
            data_df.to_excel(writer, startrow=0, startcol=0)
        not_data_df = pd.DataFrame(not_data_lt)
        with pd.ExcelWriter(rf"tools/标准号1_urls_获取失败.xlsx") as writer:
            not_data_df.to_excel(writer, startrow=0, startcol=0)
        return data_df

    def calculate(self):
        data_df = self.visit_real()


if __name__ == '__main__':
    obj = FoundationData()
    obj.calculate()
