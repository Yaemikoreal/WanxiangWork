from bs4 import BeautifulSoup
from PIL import Image
import re


def cut_pic(x, y, filename):
    img1 = Image.open('下载文件/' + filename + '.png')
    # x=480
    # y=1183
    crop_area = (x, y, x + 119, y + 168)
    # 裁剪图片
    cropped_img = img1.crop(crop_area)
    # 保存裁剪后的图片
    # cropped_img.save('测试裁剪.png')
    return cropped_img


def process_file(source):
    """
    从 HTML 源代码中提取页面 ID 和文件名，并根据图片位置信息裁剪并组合图片。

    :param source: HTML 源代码字符串
    :return: 最后处理的页面 ID
    """
    # 使用 BeautifulSoup 解析 HTML 源代码
    soup = BeautifulSoup(source, 'html.parser')

    # 查找所有具有 class="page" 的 div 元素
    divs = soup.find_all('div', class_='page')

    # 定义正则表达式模式
    find_file_and_id = re.compile(r'<div bg="viewGbImg.*?fileName=(?P<filename>.*?)".*?id="(?P<page_id>.*?)"')
    find_span_info = re.compile(r'<span class="(?P<place>.*?)" style="background-position: (?P<x_and_y>.*?);')

    for div in divs:
        div_str = str(div)

        # 提取页面 ID 和文件名
        result2 = find_file_and_id.search(div_str)
        if result2:
            filename = result2.group('filename')
            page_id = result2.group('page_id')
            print(f"filename, page_id: {filename, page_id}")

            # 提取 span 元素中的位置信息
            results = find_span_info.finditer(div_str)
            num = 0
            for match in results:
                x, y = match.group('x_and_y').split(' ')[0].lstrip('-').rstrip('px'), \
                       match.group('x_and_y').split(' ')[1].lstrip('-').rstrip('px')
                # print(f"x, y: {x, y}")
                little_pic = cut_pic(int(x), int(y), filename)

                if num == 0:
                    # 创建一个初始图片来操作
                    place = match.group('place')
                    x_target, y_target = get_target_position(place)
                    background_img = Image.open('tools/white_background.png')
                    image_to_place = little_pic
                    position = (x_target, y_target)
                    background_img.paste(image_to_place, position)
                    background_img.save(f'下载文件/{page_id}.png')
                else:
                    # 已经有初始图片的情况下进行操作
                    background_img = Image.open(f'下载文件/{page_id}.png')
                    place = match.group('place')
                    x_target, y_target = get_target_position(place)
                    image_to_place = little_pic
                    position = (x_target, y_target)
                    background_img.paste(image_to_place, position)
                num += 1

            # 最终保存处理后的图片
            try:
                background_img.save(f'下载文件/{page_id}.png')
            except Exception as e:
                print(f'当前附件的图片可能有问题，跳过本次下载，需要手动查看: {e}')

    return page_id

def get_target_position(place):
    """
    从 place 字符串中提取 x_target 和 y_target 的坐标。

    :param place: 包含位置信息的字符串
    :return: (x_target, y_target) 坐标元组
    """
    x_target, y_target = map(int, place.split('-')[-2:])
    x_target = int(x_target / 10 * 1190) if x_target != 0 else 0
    y_target = int(y_target / 10 * 1680) if y_target != 0 else 0
    return x_target, y_target

#3.780991315841675
#1.0094707012176514z
