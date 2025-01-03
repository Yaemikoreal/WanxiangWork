import os
import random
import re
import shutil
import time

import ddddocr
import pandas as pd
import requests
from PIL import Image
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from DrissionPage import ChromiumPage, ChromiumOptions

from ProcessPictures import process_file

# 创建浏览器对象并设置选项
options = ChromiumOptions()
options.headless = False  # 设置无头模式


"""
该脚本用于获取对应标准的附件，并对其进行拼接。
"""

class DataGet:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Cookie': 'Hm_lvt_50758913e6f0dfc9deacbfebce3637e4=1717379125; Hm_lpvt_50758913e6f0dfc9deacbfebce3637e4=1717558686; JSESSIONID=12C7E253ECC5428DA27CC601E5DD0C62'
        }
        self.session = None
        self.url_info = None
        self.brower = ChromiumPage(options)

    def can_be_download(self, openstd_id):
        urla = 'https://openstd.samr.gov.cn/bzgk/gb/std_list?p.p1=0&p.p90=circulation_date&p.p91=desc&p.p2='
        print(f"正在访问: [{urla + openstd_id}]")
        try:
            self.brower.get(url=urla + openstd_id)
            resp = self.brower.html
            soup = BeautifulSoup(resp, 'html.parser')
            td = soup.find('td', style="text-align: left;")
            result = re.findall("onclick=.*?showInfo.*?'(?P<a>.*?)'", str(td))
            print(result[0])
            self.url_info = 'https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=' + result[0]
            self.brower.get( self.url_info)
            resp = self.brower.html
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
            return False, False

    def get_session(self, url):
        """
        获得session进行后续处理
        """
        max_retries = 2
        while max_retries > 0:
            try:
                resp = requests.get(url, timeout=15)
                self.session = resp.cookies
                self.session = str(self.session.values()).replace('[', '').replace(']', '').replace("'", '')
                resp.close()
                print("[session] 获取完毕")
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
                resp = requests.get(url, headers=header, timeout=15)
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

    def code_yz(self):
        # 验证码识别
        with open('tools/pic.jpg', 'rb') as read_pic:
            img_bytes = read_pic.read()
            code = ocr.classification(img_bytes)
            print(f"验证码识别: {code}")
            return code

    def get_qr_code_new(self, src):
        new_url = rf"http://c.gb688.cn/bzgk/gb/{src}"
        header = {
            "Cookie": "JSESSIONID=" + self.session
        }
        max_retries = 3
        while max_retries > 0:
            try:
                resp = requests.get(new_url, headers=header, timeout=15)
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
    def check_code_new(self,download_url, title, number):
        button = self.brower.ele('@text():下载标准')
        button.click()
        self.brower.wait(random.uniform(0.5, 1))
        self.brower=self.brower.latest_tab
        button_download = self.brower.ele('css:img[src][onclick]')
        button_download.click()
        time.sleep(2)
        soup = BeautifulSoup(self.brower.html,"html.parser")
        tag = soup.find('img',attrs={"class":"verifyCode"})
        src = tag.get('src')
        # code_new = self.get_qr_code_new(src)
        # 对整页截图并保存
        bytes_str =  tag.get_screenshot(path='tools', name='pic.jpg', full_page=True)
        input_button = self.brower.ele('css:input[id="verifyCode"]')
        input_button.input(code_new)
        button_yz = self.brower.ele("css:button[class='btn btn-primary']")
        button_yz.click()
        pass

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
                response = requests.post(verify_url, headers=headers, data=data, timeout=15)
                print(f"验证码和下载链接: {response.text, response.headers}")
                if response.text != "success":
                    print(response.content)
                    print('验证码发送错误，可能是识别错误')
                    return False
                page_source = requests.get(download_url, headers=headers, timeout=15)
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
                        download_pdf = requests.get(download_pageurl, headers=headers, timeout=15)
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
        # 下载结果储存路径
        pdf_file_path = rf"E:/JXdata/处理完成的pdf/{title}.pdf"
        # self.create_pdf(pdf_file_path, page)
        self.images_to_pdf(images_folder="单页/", output_pdf=pdf_file_path)
        # 删除文件
        self.delete_files('下载文件/')
        self.delete_files('裁剪的系列图片/')
        self.delete_files('单页/')
        print(f"标准 [{title}] 处理完毕!!!")
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
        print("开始读取标准号")
        standard_df = pd.read_excel('tools/标准号.xlsx')
        existing_files = set(os.listdir(r"E:/JXdata/处理完成的pdf/"))
        try:
            for index, row in standard_df.iterrows():
                title = row['Name']
                number = row['Code']
                print(f'标题 {title}  标准号为 {number}')
                filename = number + ".pdf"
                # if filename in existing_files:
                #     print("该标准文件已经存在!!!")
                #     continue
                # 返回是否可以下载的状态以及网站相应的名字
                file_can_download, file_name = self.can_be_download(number)

                if file_can_download and file_name:
                    time.sleep(random.uniform(2, 5))
                    # 如果可以下载，则根据file_name构造对应的URL
                    url = f'http://c.gb688.cn/bzgk/gb/showGb?type=online&hcno={file_name}'
                    # 尝试最多五次获取验证码并验证
                    for retry in range(5):
                        # 获取session会话
                        self.get_session(url)
                        # download_status = self.check_code(self.get_qr_code(), url)
                        download_status = self.check_code_new(url, title, number)
                        # 如果验证码正确则退出循环
                        if download_status:
                            print("=====" * 30)
                            break
                        print(f"sleep 然后进行下一次尝试 [{retry + 1}]")
                        print("=====" * 30)
                        time.sleep(random.uniform(3, 5))
        finally:
            self.brower.quit()


if __name__ == '__main__':
    obj = DataGet()
    obj.calculate()
