import os
import random
import re
import shutil
import time
import cv2
import fitz
import numpy as np
from reportlab.lib.pagesizes import A4
import ddddocr
import pandas as pd
import requests
from bs4 import BeautifulSoup
from reportlab.pdfgen import canvas
from selenium import webdriver
from ProxyTesting import test_ip
from ProcessPictures import process_file
from PIL import Image

web = webdriver.Firefox()


class DataGet():
    def __init__(self):
        self.proxies = dict(http='http://183.159.204.186:10344', https='http://183.159.204.186:10344')
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1717379125; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1717558686; JSESSIONID=12C7E253ECC5428DA27CC601E5DD0C62'
        }
        self.proxies_url = "http://route.xiongmaodaili.com/xiongmao-web/api/glip?secret=b9200c80d01ddc746e97430b3d4a46a9&orderNo=GL202403191725045jqovn7t&count=1&isTxt=0&proxyType=1&returnAccount=1"
        self.session = None

    def get_new_proxies(self):
        """
        获取更新可用代理IP
        :return:
        """
        max_retries = 3
        while max_retries > 0:
            try:
                response = requests.get(self.proxies_url, headers=self.headers, timeout=15)
                data_js = response.json()
                proxie_dt = data_js.get('obj')[0]
                proxies_ip = proxie_dt.get('ip')
                proxies_port = proxie_dt.get('port')
                ip = f'http://{proxies_ip}:{proxies_port}'
                self.proxies = dict(http=ip, https=ip)
                print("代理更换完毕!")
                break
            except Exception as e:
                max_retries -= 1
                print(f"[proxies] 剩余重试次数:[{max_retries}],错误: {e}")
                time.sleep(random.uniform(1, 2))
                continue

    def can_be_download(self, openstd_id):
        urla = 'https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2='
        print(f"正在访问: [{urla + openstd_id}]")
        try:
            web.get(url=urla + openstd_id)
            resp = web.page_source
            soup = BeautifulSoup(resp, 'html.parser')
            td = soup.find('td', style="text-align: left;")
            result = re.findall("onclick=.*?showInfo.*?'(?P<a>.*?)'", str(td))
            # print(result[0])
            url_info = 'https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=' + result[0]
            web.get(url_info)
            resp = web.page_source
            soup = BeautifulSoup(resp, 'html.parser')
            if_down_load = str(soup.find('td', style="padding-top:20px;").get_text())
            # print(if_down_load)
            if '在线预览' in if_down_load or '下载标准' in if_down_load:
                print('可以下载附件,进行下载')
                return True, result[0]
            else:
                print('无法下载')
                return False, result[0]
        except Exception as e:
            print('可能是网络出现错误', e)

    def get_session(self, url):
        """
        获得session进行后续处理
        """
        max_retries = 1
        while max_retries > 0:
            try:
                resp = requests.get(url, proxies=self.proxies, timeout=15)
                self.session = resp.cookies
                self.session = str(self.session.values()).replace('[', '').replace(']', '').replace("'", '')
                resp.close()
                break
            except Exception as e:
                max_retries -= 1
                print(f"[session] 剩余重试次数:[{max_retries}],错误: {e}")
                time.sleep(random.uniform(1, 2))
                continue

    def get_qr_code(self):
        """
        验证码识别的函数，有小概率识别失败
        """
        # 该网站如果不发起刷新请求，那么验证码就会固定，每次所需要的验证码都是相同的
        time_stamp = str(time.time()).replace('.', '')[0:13]
        url = f'http://c.gb688.cn/bzgk/gb/gc?_{time_stamp}'
        header = {
            "Cookie": "JSESSIONID=" + self.session
        }
        max_retries = 3
        while max_retries > 0:
            try:
                resp = requests.get(url, proxies=self.proxies, headers=header, timeout=15)
                resp.raise_for_status()  # 检查响应状态码

                # 保存验证码图片
                with open('tools/code_t.jpg', 'wb') as save_code:
                    save_code.write(resp.content)

                # 初始化OCR对象
                ocr = ddddocr.DdddOcr()

                # 验证码识别
                with open('tools/code_t.jpg', 'rb') as read_pic:
                    img_bytes = read_pic.read()
                    code = ocr.classification(img_bytes)
                    print(f"验证码识别: {code}")
                    return code

            except requests.exceptions.RequestException as e:
                print(f"请求失败，剩余重试次数: [{max_retries - 1}], 错误信息: {e}")
                max_retries -= 1
                if max_retries > 0:
                    # 等待后重试
                    time.sleep(random.uniform(2, 4))
                else:
                    print("所有重试均失败。")
                    return None

    def check_code(self, code, download_url):
        """
        验证验证码并下载指定的 PDF 文件。

        :param code: 验证码
        :param download_url: 下载链接
        :return: 成功或失败的布尔值
        """
        verify_url = f"http://c.gb688.cn/bzgk/gb/verifyCode?verifyCode={code}"
        headers = {
            "Cookie": f"JSESSIONID={self.session}"
        }
        data = {}
        soup = None
        max_retries = 3
        while max_retries > 0:
            try:
                response = requests.post(verify_url, headers=headers, proxies=self.proxies, data=data, timeout=15)
                print(f"验证码和下载链接: {response.text, response.headers}")
                if response.text != "success":
                    print(response.content)
                    print('验证码发送错误，可能是识别错误')
                    return False
                page_source = requests.get(download_url, headers=headers, proxies=self.proxies, timeout=15)
                if page_source.status_code == 200:
                    soup = BeautifulSoup(page_source.text, 'html.parser')
                if soup:
                    break
            except requests.exceptions.RequestException as e:
                print(f"请求失败，剩余重试次数: [{max_retries - 1}], 错误信息: {e}")
                max_retries -= 1
                if max_retries > 0:
                    # 等待后重试
                    time.sleep(random.uniform(3, 5))
                else:
                    print("所有重试均失败。")
                    # 更换代理
                    self.get_new_proxies()
                    time.sleep(random.uniform(0.5, 1))
                    # 获取session会话
                    self.get_session(download_url)
                    return False
        time.sleep(1)

        if not soup:
            print("获取soup为空!")
        title = soup.find('title').get_text().split('|')[-1].replace('/', '-')
        print(f"title: {title}")

        viewer_div = soup.find('div', id='viewer', class_='pdfViewer')
        if viewer_div is None:
            print("未找到 viewer 分区")
            return False

        find_pattern = re.compile(r'<div bg="(?P<filename>.*?)".*?id="(?P<id>.*?)".*?>')
        results = find_pattern.finditer(str(viewer_div))
        file_name_old = ''
        num = 0

        for match in results:
            file_name_new = match.group('filename')
            if file_name_new != file_name_old:
                file_name_download = file_name_new.split('=')[-1]
                download_pageurl = f'http://c.gb688.cn/bzgk/gb/viewGbImg?fileName={file_name_download}'
                max_retries = 3
                while max_retries > 0:
                    try:
                        download_pdf = requests.get(download_pageurl, proxies=self.proxies, headers=headers, timeout=15)
                        print(f'download_pdf状态: {download_pdf.status_code}')
                        print('字节长度:' + str(len(download_pdf.content)))

                        if len(download_pdf.content) != 0:
                            with open(f'下载文件/{file_name_download}.png', 'wb') as file:
                                file.write(download_pdf.content)
                            print(f'[下载文件/{file_name_download}.png] 保存完毕!')
                            break
                        else:
                            print('下载出错,检查到文章字节数为0')
                            continue
                    except requests.exceptions.RequestException as e:
                        print(f"请求失败，剩余重试次数: [{max_retries - 1}], 错误信息: {e}")
                        max_retries -= 1
                        if max_retries > 0:
                            # 等待后重试
                            time.sleep(random.uniform(2, 4))
                        else:
                            print("所有重试均失败。")
                            return None

                num += 1
                file_name_old = file_name_new
                time.sleep(random.uniform(1, 4))

        page = process_file(str(viewer_div))
        pdf_file_path = f"处理完成的pdf/{title}.pdf"
        # self.create_pdf(pdf_file_path, page)
        self.images_to_pdf(images_folder="单页/", output_pdf=pdf_file_path)
        # 删除文件
        self.delete_files('下载文件/')
        self.delete_files('裁剪的系列图片/')
        self.delete_files('单页/')
        return True

    def delete_files(self, folder_path):
        """
        删除指定文件夹下的所有文件和子目录。

        :param folder_path: 文件夹路径
        """
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

            for name in dirs:
                dir_path = os.path.join(root, name)
                try:
                    shutil.rmtree(dir_path)
                except Exception as e:
                    print(f'Failed to delete {dir_path}. Reason: {e}')
        print(f"已删除 {folder_path} !")

    def images_to_pdf(self, images_folder, output_pdf):
        """
        将指定文件夹内的所有图片文件合并成一个PDF文件，每张图片占据一个PDF页面，并按文件名中的数字顺序排列。

        :param images_folder: 包含图片文件的文件夹路径
        :param output_pdf: 输出的PDF文件路径
        """
        # 获取文件夹内所有的图片文件名
        image_files = [f for f in os.listdir(images_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

        # 按文件名中的数字排序
        image_files.sort(key=lambda x: int(x.split('.')[0]))

        # 创建一个PDF画布
        c = canvas.Canvas(output_pdf, pagesize=A4)

        # 固定目标尺寸，这里使用A4纸张的标准尺寸
        target_width, target_height = A4

        for image_file in image_files:
            img_path = os.path.join(images_folder, image_file)
            try:
                # 打开图片
                with Image.open(img_path) as img:
                    # 获取图片的宽度和高度
                    img_width, img_height = img.size

                    # 计算图片与目标尺寸的比例，选择较小的比例值来保持图片原始比例
                    ratio_w = target_width / img_width
                    ratio_h = target_height / img_height
                    ratio = min(ratio_w, ratio_h)

                    # 调整图片大小以适应目标尺寸，同时保持原始比例
                    new_img_width = img_width * ratio
                    new_img_height = img_height * ratio

                    # 计算图片在页面上的位置，使其居中
                    x = (target_width - new_img_width) / 2
                    y = (target_height - new_img_height) / 2

                    # 在当前页面上绘制图片
                    c.drawImage(img_path, x, y, width=new_img_width, height=new_img_height)

                    # 开始新的页面
                    c.showPage()
            except IOError:
                print(f"无法打开图片文件 {img_path}")

        # 保存PDF文件
        c.save()

    def calculate(self):
        file_name = None

        num = 1
        standard_df = pd.read_excel('tools/标准号1.xlsx')
        # 通过iloc函数从第num行开始读取最多60行数据，并使用for循环遍历这些数据
        for index, row in standard_df.iloc[num:num + 60].iterrows():  # 设置每次读取的数据量
            title = row['Name']
            number = row['Code']
            # 打印出当前标题和标准号的信息
            print(f'标题 {title}  标准号为 {number}')
            filename = number + ".pdf"
            file_path = os.path.join("处理完成的pdf/", filename)
            file_status = os.path.isfile(file_path)
            if file_status:
                print("该标准文件已经存在!!!")
                continue
            try:
                # 调用can_be_download函数，返回是否可以下载的状态以及网站相应的名字
                file_can_download, file_name = self.can_be_download(number)
            except Exception as e:
                print(e)
                file_can_download = False
            # 每处理完一条数据，num加一
            num += 1
            time.sleep(random.uniform(2, 8))
            if file_can_download and file_name:
                if not test_ip(self.proxies):
                    # 更换代理
                    self.get_new_proxies()
                # 如果可以下载，则根据file_name构造对应的URL
                url = f'http://c.gb688.cn/bzgk/gb/showGb?type=online&hcno={file_name}'
                # url = f"http://c.gb688.cn/bzgk/gb/showGb?type=download&hcno={file_name}"
                # 获取session会话
                self.get_session(url)
                # 尝试最多五次获取验证码并验证
                for retry in range(5):
                    if not test_ip(self.proxies):
                        # 尝试更换代理
                        self.get_new_proxies()
                        # 获取session会话
                        self.get_session(url)
                    # 如果验证码正确则退出循环
                    if self.check_code(self.get_qr_code(), url):
                        break
                    else:
                        # 如果验证码不正确，则重新获取验证码并验证
                        self.check_code(self.get_qr_code(), url)
                    print("sleep 然后进行下一次尝试")
                    time.sleep(random.uniform(3, 5))

        # 存储次数，下次从结束的地方开始
        with open('tools/count.txt', 'w') as file:
            file.write(str(num))


# 推标需要使用和网页一样的css样式进行切割background-position为切割位置  pdfImg为放置位置   以白色为底，将图片放入对应的地方

if __name__ == '__main__':
    obj = DataGet()
    obj.calculate()
