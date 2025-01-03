import random
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
import PriceQuery
import PublicFunction as pf

"""
该方法用于 自动化获取标准号，并对标准号及其基础信息进行入库
输出内容位于“标准号1.xlsx”
"""

class DataGetTab:
    def __init__(self):
        self.url = 'https://openstd.samr.gov.cn/bzgk/gb/std_list_type?r=0.3466977741726638&page=1&pageSize=50&p.p1=1&p.p7=0.25&p.p90=circulation_date&p.p91=desc'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
            'Cookie': f'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1720497603,1720578380; HMACCOUNT=3F828CD7B7E5790B; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1720598679; JSESSIONID=D9CAD23B7416CDBE7F1C678CB80AD7B0',
            'host': 'openstd.samr.gov.cn'
        }
        # 插入sql
        self.sql = """
                INSERT INTO [dbo].[标准库]
                (
                    [唯一标志],
                    [标题],
                    [全文],
                    [发布部门],
                    [发布日期],
                    [实施日期],
                    [标准状态],
                    [标准状态key],
                    [中国标准分类号],
                    [国际标准分类号],
                    [标准号],
                    [附件位置],
                    [来源],
                    [价格],
                    [是否免费]
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """
        # 数据列表
        self.data_lt = []
        # 计数器
        self.count_num = 0
        # 错误计数器
        self.error_count_num = 0

    def mark_and_date(self, web, i):
        # 获取当前日期
        current_date = datetime.now()
        # 格式化日期为"年月日"形式
        formatted_date = current_date.strftime("%Y%m%d")
        # 唯一标志
        only_biaozhi = 'gbbz' + formatted_date

        # 等待元素出现
        wait = WebDriverWait(web, 10)
        info_xpath = f'//*[@id="stage"]/div/div[2]/div/div/div/div[2]/table/tbody[2]/tr[{i}]/td[4]/a'
        info_element = wait.until(EC.presence_of_element_located((By.XPATH, info_xpath)))

        # 标准名称
        titles = info_element.text
        js = str(info_element.get_attribute('onclick'))

        # 提取 hcno 值
        match = re.search(r"'(.*?)'", js)
        if match:
            js_value = match.group(1)
            only_biaozhi += js_value[:10]
            link = f'https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno={js_value}'
            print(f"标题: [{titles}], 链接: [{link}], 编号: [{js_value}]")
            return titles, only_biaozhi, js_value, link
        else:
            print("未找到 hcno 值")
            return None, None, None, None

    def shishi_status_get(self, info):
        # 获取实施状态
        status_xpath = '/html/body/div[2]/div/div/div/div/table[2]/tbody/tr[3]/td/span'
        status_element = info.find_element(By.XPATH, status_xpath)
        shiShi_Status = status_element.text
        # 实施状态Key
        if shiShi_Status == '即将实施':
            shiShi_Status_Key = '02'
        elif shiShi_Status == '现行有效':
            shiShi_Status_Key = '01'
        else:
            shiShi_Status_Key = '00'
        print(f"实施状态: [{shiShi_Status}], 实施状态Key值: [{shiShi_Status_Key}]")
        return shiShi_Status, shiShi_Status_Key

    def full_filter(self, web, biaozhunhao, titles):
        # 获取全文文本
        text = web.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/table[2]/tbody/tr[4]/td/span').text
        # text = web.find_element_by_xpath('/html/body/div[2]/div/div/div/div/table[2]/tbody/tr[4]/td/span').text
        # 判断文本中是否包含特定字符串
        if '该推荐性标准采用了ISO、IEC等国际国外组织的标准' in text:
            # 如果包含, 则设置一个预定义的 HTML 字符串作为全文内容, 并设置附件为空字符串
            full = f'''
                    <p>该推荐性标准采用了ISO、IEC等国际国外组织的标准，由于涉及版权保护问题，本系统暂不提供在线阅读服务。如需正式标准出版物，请联系 400 902 6766 或扫描下方二维码添加客服微信。</p><p style="text-align:center;"><img width="30%" src="/datafolder/附件/新版标准/国家标准/wx01.png"/></p>
                    '''.strip()
            fujian = ''
        else:
            # 如果不包含, 则设置附件路径, 并生成一个带有标准号和标题的 HTML 链接作为全文内容
            fujian = f'/国家标准/{biaozhunhao}.pdf'
            full = '<a href="javascript:void(0)" class="" onclick="pdfck()">' + str(biaozhunhao) + ' ' + str(
                titles) + '</a>'
        return full, fujian

    def standard_classification_number(self, info):
        # 获取中国标准分类号文本内容
        cn_FenLei = '/html/body/div[2]/div/div/div/div/div[2]/div[2]'
        status_element = info.find_element(By.XPATH, cn_FenLei)
        cn_FenLei = status_element.text
        # 获取国际标准分类号的文本内容
        native_FenLei = info.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div[2]/div[4]').text
        print(f"中国标准分类号: [{cn_FenLei}], 国际标准分类号: [{native_FenLei}]")
        return cn_FenLei, native_FenLei

    def get_date_all(self, info):
        # 获取发布日期, 其中的 '-' 替换成 '.'
        fabu_Date = info.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div[3]/div[2]').text
        fabu_Date = str(fabu_Date.replace('-', '.'))
        # 获取实施日期, 将 '-' 替换成 '.'
        shiShi_Date = info.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div[3]/div[4]').text
        shiShi_Date = str(shiShi_Date.replace('-', '.'))
        # 获取发布部门名称
        faBu_PartMent = info.find_element(By.XPATH, '/html/body/div[2]/div/div/div/div/div[5]/div[2]').text
        print(f"发布日期: [{fabu_Date}], 实施日期: [{shiShi_Date}], 发布部门: [{faBu_PartMent}]")
        return fabu_Date, shiShi_Date, faBu_PartMent

    def price_acquisition(self, biaozhunhao):
        # 调用价格查询函数获取价格
        sell = PriceQuery.get_Sell(biaozhunhao=biaozhunhao)
        # 设置是否免费标记为默认值
        isFree = '001'
        # 判断价格是否为零
        if int(sell) != 0:
            # 如果价格不为零, 更改是否免费标记
            isFree = '002'
        print(f"标准价格: [{sell}], 是否免费: [{isFree}]")
        return sell, isFree

    def existence_judgment(self, biaozhunhao):
        """
        对该标准号进行判断，如果存在于库则返回False,如果不存在于库则返回True
        :param biaozhunhao: 标准号
        :return: 存在与否的布尔值
        """
        sql = rf"SELECT * FROM [自收录数据].dbo.[标准库] WHERE [标准号] = '{biaozhunhao}'"
        results = pf.query_sql_BidDocument(sql)
        if len(results) == 0:
            return True
        return False

    def calculate(self):
        # 创建Firefox的Options对象
        options = Options()
        options.headless = True
        # 使用Options对象创建Firefox WebDriver
        web = webdriver.Firefox(options=options)

        # 打开网页
        web.get(self.url)

        for i in range(1, 60):
            try:
                time.sleep(random.uniform(1, 2))
                # 等待页面加载完成，直到元素可见
                wait = WebDriverWait(web, 10)
                element = wait.until(EC.presence_of_element_located(
                    (By.XPATH, f'//*[@id="stage"]/div/div[2]/div/div/div/div[2]/table/tbody[2]/tr[{i}]/td[2]/a')))
                # 标准号
                biaozhunhao = element.text
                # 该标准的存在性判断
                if not self.existence_judgment(biaozhunhao):
                    print(f"[{biaozhunhao}] 该标准已经存在于库!")
                    print("====" * 20)
                    continue
                self.count_num += 1
                print(f"现在是[{self.count_num}]号数据:")
                # 获取 标题, 标准正文, 访问页面url
                titles, only_biaozhi, js, link = self.mark_and_date(web, i)

                web.get(link)
                info_xpath = '/html/body/div[2]/div/div/div/div'
                info_element = wait.until(EC.presence_of_element_located((By.XPATH, info_xpath)))
                # info = web.find_element_by_xpath('/html/body/div[2]/div/div/div/div')
                # 获取 实施状态 以及 实施状态Key值
                shiShi_Status, shiShi_Status_Key = self.shishi_status_get(info_element)
                # 中国标准分类号 以及 国际标准分类号
                cn_FenLei, native_FenLei = self.standard_classification_number(info_element)
                # 获取 发布日期，实施日期，发布部门
                fabu_Date, shiShi_Date, faBu_PartMent = self.get_date_all(info_element)
                # 正文 以及 附件
                full, fujian = self.full_filter(web, biaozhunhao, titles)
                # 价格查询计算，是否免费
                sell, isFree = self.price_acquisition(biaozhunhao)
                # 准备要插入的数据
                data = (
                    only_biaozhi, titles, full, faBu_PartMent, fabu_Date, shiShi_Date, shiShi_Status, shiShi_Status_Key,
                    cn_FenLei,
                    native_FenLei, biaozhunhao, fujian, '新版标准库', sell, isFree)
                pf.save_sql_BidDocument(sql=self.sql, params=data)
                # 打印提示信息
                print('已提交')
                self.data_lt.append({"Name": titles, "Code": biaozhunhao})
                print("====" * 20)
                web.back()

            except Exception as e:
                self.error_count_num += 1
                if self.error_count_num == 10:
                    print("抓取完毕")
                    break
                print(e)
                continue
        web.close()
        data_df = pd.DataFrame(self.data_lt)
        # 写入 Excel 文件
        output_file = 'tools/标准号1.xlsx'
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            data_df.to_excel(writer, sheet_name='Sheet1', index=False)
        print(f"标准号数据写入到: [{output_file}]")


if __name__ == '__main__':
    obj = DataGetTab()
    obj.calculate()
