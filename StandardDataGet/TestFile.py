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
    cropped_img.save('测试裁剪.png')
    return cropped_img


def process_file(source):
    """
    从 HTML 源代码中提取页面 ID 和文件名，并根据图片位置信息裁剪并组合图片。

    :param source: HTML 源代码字符串
    :return: 最后处理的页面 ID
    """
    page_count_id = 0
    # 使用 BeautifulSoup 解析 HTML 源代码
    soup = BeautifulSoup(source, 'html.parser')

    # 查找所有具有 class="page" 的 div 元素
    divs = soup.find_all('div', class_='page')

    for div in divs:
        page_count_id += 1
        filename = div['bg'].lstrip('viewGbImg?').lstrip('fileName=')
        page_id = div['id']
        span_all = div.find_all('span')
        num = 0
        for span in span_all:
            place = span['class']
            x_and_y = span['style'].lstrip('background-position: ')
            # 移除字符串末尾的分号,按空格分割字符串
            x_and_y = x_and_y.rstrip(';').split()
            # 提取 x 和 y 值
            x = int(x_and_y[0].rstrip('px'))
            y = int(x_and_y[1].rstrip('px').lstrip("-"))
            little_pic = cut_pic(x, y, filename)
            if num == 0:
                # 创建一个初始图片来操作
                background_img = Image.open('tools/white_background.png')
                x_target, y_target = get_target_position(place)
                position = (x_target, y_target)
                background_img.paste(little_pic, position)
                background_img.save(f'下载文件/{page_id}.png')
            else:
                # 已经有初始图片的情况下进行操作
                background_img = Image.open(f'下载文件/{page_id}.png')
                x_target, y_target = get_target_position(place)
                position = (x_target, y_target)
                background_img.paste(little_pic, position)
                background_img.save(f'下载文件/{page_id}.png')
            num += 1

    return page_count_id

def get_target_position(place):
    """
    从 place 字符串中提取 x_target 和 y_target 的坐标。

    :param place: 包含位置信息的字符串
    :return: (x_target, y_target) 坐标元组
    """
    place = str(place[0])
    x_target, y_target = map(int, place.split('-')[-2:])
    x_target = int(x_target / 10 * 1190) if x_target != 0 else 0
    y_target = int(y_target / 10 * 1680) if y_target != 0 else 0
    return x_target, y_target

#3.780991315841675
#1.0094707012176514z
