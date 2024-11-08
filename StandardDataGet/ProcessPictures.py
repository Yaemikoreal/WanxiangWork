import math
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageDraw
import re
import os


def cut_pic(x, y, filename, page_count_id, x_target, y_target, y_height):
    """
    根据指定的坐标裁剪图片并保存。

    :param x: 图片裁剪的起始横坐标
    :param y: 图片裁剪的起始纵坐标
    :param filename: 要裁剪的图片文件名
    :return: 裁剪后的图片对象
    """
    # 构建图片路径
    image_path = os.path.join('下载文件', f'{filename}.png')
    # 构建保存路径
    save_path = f"裁剪的系列图片/P{page_count_id}/"
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 打开图片
    with Image.open(image_path) as img:
        img_x, img_y = img.size

        # 定义裁剪区域
        crop_area = (x, y, x + img_x / 10, y + img_y / y_height)
        # 进行裁剪
        cropped_img = img.crop(crop_area)

        if not os.path.exists(save_path):
            os.makedirs(save_path)
        output_path = os.path.join(save_path, f'img_{x_target, y_target}.png')
        file_status = os.path.exists(output_path)
        if not file_status:
            # 保存裁剪后的图片
            cropped_img.save(output_path)
            # print(f"{output_path} 已保存")
    return


def calculate_height(data_page_dt):
    new_page_dt = {}
    for key, value in data_page_dt.items():
        # 计算高度除以 10 并向上取整
        height_num = math.ceil(value / 10)
        new_page_dt[key] = height_num

    return new_page_dt


def process_file(source):
    """
    从 HTML 源代码中提取页面 ID 和文件名，并根据图片位置信息裁剪图片。

    :param source: HTML 源代码字符串
    :return: 最后处理的页面 ID
    """
    page_count_id = 0
    soup = BeautifulSoup(source, 'html.parser')
    divs = soup.find_all('div', class_='page')
    data_lt = []
    data_page_dt = {}
    for div in divs:
        page_count_id += 1
        # 提取文件名
        filename_match = re.search(r'viewGbImg\?fileName=(.*?)$', div['bg'])
        filename = filename_match.group(1) if filename_match else ''
        # 查找所有的 <span> 元素
        span_all = div.find_all('span', style=True)
        num = 0
        for span in span_all:
            # 提取背景位置
            x_and_y = span['style'].lstrip('background-position: ').rstrip(';')
            x_and_y_parts = x_and_y.split()
            x = int(x_and_y_parts[0].rstrip('px').lstrip("-"))
            y = int(x_and_y_parts[1].rstrip('px').lstrip("-"))
            # 裁剪图片提取 x_target 和 y_target 的坐标
            x_target, y_target = map(int, span['class'][0].split('-')[-2:])
            data_dt = {
                "x": x,
                "y": y,
                "x_target": x_target,
                "y_target": y_target,
                "page_count_id": page_count_id,
                "filename": filename
            }
            data_lt.append(data_dt)
            num += 1
    # 计算出每张素材图片的高度
    for it in data_lt:
        filename = it.get('filename')
        if filename not in data_page_dt:
            data_page_dt[filename] = 1
        else:
            data_page_dt[filename] += 1
    data_page_dt = calculate_height(data_page_dt)

    x_y_dt = {}
    for it in data_lt:
        page_count_id = it.get('page_count_id')
        x_target = it.get('x_target')
        y_target = it.get('y_target')
        if page_count_id not in x_y_dt:
            x_y_dt[page_count_id] = [[x_target, y_target]]
        else:
            x_y_dt[page_count_id].append([x_target, y_target])

    pin_dt = {}
    # 剪切图片
    for it in data_lt:
        x = it.get('x')
        y = it.get('y')
        page_count_id = it.get("page_count_id")
        x_target = it.get('x_target')
        y_target = it.get('y_target')
        filename = it.get('filename')
        y_height = data_page_dt.get(filename)
        # 构建图片路径
        image_path = os.path.join('下载文件', f'{filename}.png')
        # 打开图片
        with Image.open(image_path) as img:
            img_x, img_y = img.size
            min_x = img_x / 10
            min_y = img_y / y_height
        cut_pic(x, y, filename, page_count_id, x_target, y_target, y_height)
        if page_count_id not in pin_dt:
            pin_dt[page_count_id] = {"min_x": min_x, "min_y": min_y}
    # 拼接图片
    for page_count_id, min_dt in pin_dt.items():
        min_x = min_dt.get('min_x')
        min_y = min_dt.get('min_y')
        x_y_lt = x_y_dt.get(page_count_id)
        pin_img(tile_width=min_x, tile_height=min_y, page_count_id=page_count_id, coordinates=x_y_lt)

    return page_count_id


def pin_img(coordinates, tile_width, tile_height, page_count_id, padding=0):
    """
    将多个小图片拼接成一张大图，避免边缘黑线。

    参数:
        coordinates (list of tuples): 各个小图片的位置坐标，例如 [(0, 0), (1, 0)]。
        tile_width (int): 小图片的宽度。
        tile_height (int): 小图片的高度。
        page_count_id (int): 页面编号，用于构建文件路径。
        padding (int): 小图片之间的间距，默认为0。
    """

    # 计算大图片的尺寸
    max_column = max(coord[0] for coord in coordinates) + 1
    max_row = max(coord[1] for coord in coordinates) + 1
    large_width = int(max_column * tile_width + padding * (max_column - 1))
    large_height = int(max_row * tile_height + padding * (max_row - 1))

    # 创建一个空白的大图片
    background_img = Image.new('RGBA', (large_width, large_height), color=(255, 255, 255, 255))

    # 存储未找到的文件路径
    missing_files = []

    # 遍历坐标列表，将小图片粘贴到大图片上
    for coord in coordinates:
        col, row = coord
        abs_left = int(col * (tile_width + padding))
        abs_top = int(row * (tile_height + padding))
        filepath = f"裁剪的系列图片/P{page_count_id}/img_({col}, {row}).png"

        try:
            with Image.open(filepath) as little_pic:
                # 确保小图片也是 RGBA 模式，以便正确处理透明度
                little_pic = little_pic.convert('RGBA')
                background_img.paste(little_pic, (abs_left, abs_top), little_pic)
        except FileNotFoundError:
            missing_files.append(filepath)
            continue

    if missing_files:
        print("Warning: The following files were not found:")
        for file in missing_files:
            print(file)

    # 保存结果图片
    output_path = f'单页/{page_count_id - 1}.png'
    background_img.save(output_path, format='PNG')
    print(f"单页数据已经保存至: [{output_path}]")

    return output_path, missing_files


if __name__ == '__main__':
    # 示例HTML源码
    html_source = '''
    <div class="pdfViewer" id="viewer">
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY0mseTr1p2oYf61ZLERTmqU%3D" class="page" id="0" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-4-2" style="background-position: -0px -0px;"></span>
    <span class="pdfImg-6-9" style="background-position: -464px -0px;"></span>
    <span class="pdfImg-9-8" style="background-position: -1160px -0px;"></span>
    <span class="pdfImg-2-7" style="background-position: -0px -328px;"></span>
    <span class="pdfImg-5-3" style="background-position: -232px -328px;"></span>
    <span class="pdfImg-1-8" style="background-position: -928px -328px;"></span>
    <span class="pdfImg-5-4" style="background-position: -1392px -328px;"></span>
    <span class="pdfImg-2-4" style="background-position: -2088px -328px;"></span>
    <span class="pdfImg-8-0" style="background-position: -0px -656px;"></span>
    <span class="pdfImg-2-2" style="background-position: -696px -656px;"></span>
    <span class="pdfImg-8-2" style="background-position: -1160px -656px;"></span>
    <span class="pdfImg-5-9" style="background-position: -1392px -656px;"></span>
    <span class="pdfImg-7-7" style="background-position: -1624px -656px;"></span>
    <span class="pdfImg-6-0" style="background-position: -2088px -656px;"></span>
    <span class="pdfImg-6-7" style="background-position: -696px -984px;"></span>
    <span class="pdfImg-3-9" style="background-position: -928px -984px;"></span>
    <span class="pdfImg-1-1" style="background-position: -1624px -984px;"></span>
    <span class="pdfImg-6-8" style="background-position: -2088px -984px;"></span>
    <span class="pdfImg-2-8" style="background-position: -232px -1312px;"></span>
    <span class="pdfImg-7-0" style="background-position: -464px -1312px;"></span>
    <span class="pdfImg-2-0" style="background-position: -928px -1312px;"></span>
    <span class="pdfImg-8-8" style="background-position: -1160px -1312px;"></span>
    <span class="pdfImg-4-9" style="background-position: -1392px -1312px;"></span>
    <span class="pdfImg-6-3" style="background-position: -1624px -1312px;"></span>
    <span class="pdfImg-1-2" style="background-position: -2088px -1312px;"></span>
    <span class="pdfImg-1-0" style="background-position: -696px -1640px;"></span>
    <span class="pdfImg-6-1" style="background-position: -1856px -1640px;"></span>
    <span class="pdfImg-4-7" style="background-position: -232px -1968px;"></span>
    <span class="pdfImg-6-4" style="background-position: -928px -1968px;"></span>
    <span class="pdfImg-3-8" style="background-position: -1160px -1968px;"></span>
    <span class="pdfImg-9-2" style="background-position: -1856px -1968px;"></span>
    <span class="pdfImg-7-4" style="background-position: -0px -2296px;"></span>
    <span class="pdfImg-4-1" style="background-position: -232px -2296px;"></span>
    <span class="pdfImg-7-9" style="background-position: -696px -2296px;"></span>
    <span class="pdfImg-3-2" style="background-position: -1160px -2296px;"></span>
    <span class="pdfImg-6-2" style="background-position: -1392px -2296px;"></span>
    <span class="pdfImg-7-1" style="background-position: -1624px -2296px;"></span>
    <span class="pdfImg-5-8" style="background-position: -1856px -2296px;"></span>
    <span class="pdfImg-9-1" style="background-position: -2088px -2296px;"></span>
    <span class="pdfImg-5-1" style="background-position: -928px -2624px;"></span>
    <span class="pdfImg-7-2" style="background-position: -1160px -2624px;"></span>
    <span class="pdfImg-3-3" style="background-position: -1392px -2624px;"></span>
    <span class="pdfImg-3-4" style="background-position: -1624px -2624px;"></span>
    <span class="pdfImg-5-7" style="background-position: -2088px -2624px;"></span>
    <span class="pdfImg-2-1" style="background-position: -232px -2952px;"></span>
    <span class="pdfImg-3-1" style="background-position: -464px -2952px;"></span>
    <span class="pdfImg-4-4" style="background-position: -696px -2952px;"></span>
    <span class="pdfImg-2-3" style="background-position: -1160px -2952px;"></span>
    <span class="pdfImg-4-8" style="background-position: -1392px -2952px;"></span>
    <span class="pdfImg-7-3" style="background-position: -1624px -2952px;"></span>
    <span class="pdfImg-5-2" style="background-position: -2088px -2952px;"></span>
    <span class="pdfImg-7-8" style="background-position: -0px -3280px;"></span>
    <span class="pdfImg-3-7" style="background-position: -1392px -3280px;"></span>
    <span class="pdfImg-8-1" style="background-position: -232px -3608px;"></span>
    <span class="pdfImg-4-3" style="background-position: -928px -3608px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY0mseTr1p2oYf61ZLERTmqU%3D" class="page" id="1" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-3-3" style="background-position: -696px -2624px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY0mseTr1p2oYf61ZLERTmqU%3D" class="page" id="2" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-4-1" style="background-position: -1624px -328px;"></span>
    <span class="pdfImg-7-3" style="background-position: -1856px -328px;"></span>
    <span class="pdfImg-5-3" style="background-position: -232px -656px;"></span>
    <span class="pdfImg-2-2" style="background-position: -1160px -984px;"></span>
    <span class="pdfImg-8-0" style="background-position: -1856px -984px;"></span>
    <span class="pdfImg-4-2" style="background-position: -0px -1312px;"></span>
    <span class="pdfImg-4-3" style="background-position: -696px -1312px;"></span>
    <span class="pdfImg-5-1" style="background-position: -232px -1640px;"></span>
    <span class="pdfImg-3-2" style="background-position: -464px -1640px;"></span>
    <span class="pdfImg-7-0" style="background-position: -1160px -1640px;"></span>
    <span class="pdfImg-8-3" style="background-position: -2088px -1640px;"></span>
    <span class="pdfImg-7-2" style="background-position: -464px -1968px;"></span>
    <span class="pdfImg-8-9" style="background-position: -696px -1968px;"></span>
    <span class="pdfImg-8-2" style="background-position: -1392px -1968px;"></span>
    <span class="pdfImg-1-2" style="background-position: -0px -2624px;"></span>
    <span class="pdfImg-6-3" style="background-position: -0px -2952px;"></span>
    <span class="pdfImg-6-2" style="background-position: -928px -2952px;"></span>
    <span class="pdfImg-4-4" style="background-position: -232px -3280px;"></span>
    <span class="pdfImg-3-3" style="background-position: -1160px -3280px;"></span>
    <span class="pdfImg-1-3" style="background-position: -1856px -3280px;"></span>
    <span class="pdfImg-5-2" style="background-position: -2088px -3280px;"></span>
    <span class="pdfImg-2-3" style="background-position: -0px -3608px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY0mseTr1p2oYf61ZLERTmqU%3D" class="page" id="3" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-2-3" style="background-position: -696px -3280px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY0mseTr1p2oYf61ZLERTmqU%3D" class="page" id="4" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-7-5" style="background-position: -232px -0px;"></span>
    <span class="pdfImg-5-1" style="background-position: -696px -0px;"></span>
    <span class="pdfImg-3-4" style="background-position: -928px -0px;"></span>
    <span class="pdfImg-3-2" style="background-position: -1392px -0px;"></span>
    <span class="pdfImg-7-3" style="background-position: -1624px -0px;"></span>
    <span class="pdfImg-1-5" style="background-position: -1856px -0px;"></span>
    <span class="pdfImg-4-1" style="background-position: -2088px -0px;"></span>
    <span class="pdfImg-7-0" style="background-position: -464px -328px;"></span>
    <span class="pdfImg-4-6" style="background-position: -696px -328px;"></span>
    <span class="pdfImg-6-5" style="background-position: -1160px -328px;"></span>
    <span class="pdfImg-2-5" style="background-position: -464px -656px;"></span>
    <span class="pdfImg-8-3" style="background-position: -928px -656px;"></span>
    <span class="pdfImg-2-4" style="background-position: -1856px -656px;"></span>
    <span class="pdfImg-8-2" style="background-position: -0px -984px;"></span>
    <span class="pdfImg-6-4" style="background-position: -232px -984px;"></span>
    <span class="pdfImg-6-3" style="background-position: -464px -984px;"></span>
    <span class="pdfImg-7-2" style="background-position: -1392px -984px;"></span>
    <span class="pdfImg-1-4" style="background-position: -1856px -1312px;"></span>
    <span class="pdfImg-8-9" style="background-position: -0px -1640px;"></span>
    <span class="pdfImg-7-4" style="background-position: -928px -1640px;"></span>
    <span class="pdfImg-4-4" style="background-position: -1392px -1640px;"></span>
    <span class="pdfImg-5-4" style="background-position: -1624px -1640px;"></span>
    <span class="pdfImg-8-0" style="background-position: -0px -1968px;"></span>
    <span class="pdfImg-5-5" style="background-position: -1624px -1968px;"></span>
    <span class="pdfImg-1-3" style="background-position: -2088px -1968px;"></span>
    <span class="pdfImg-5-2" style="background-position: -464px -2296px;"></span>
    <span class="pdfImg-2-2" style="background-position: -928px -2296px;"></span>
    <span class="pdfImg-1-2" style="background-position: -232px -2624px;"></span>
    <span class="pdfImg-5-3" style="background-position: -464px -2624px;"></span>
    <span class="pdfImg-3-5" style="background-position: -1856px -2624px;"></span>
    <span class="pdfImg-2-3" style="background-position: -1856px -2952px;"></span>
    <span class="pdfImg-6-2" style="background-position: -464px -3280px;"></span>
    <span class="pdfImg-4-2" style="background-position: -928px -3280px;"></span>
    <span class="pdfImg-3-3" style="background-position: -1624px -3280px;"></span>
    <span class="pdfImg-4-3" style="background-position: -464px -3608px;"></span>
    <span class="pdfImg-4-5" style="background-position: -696px -3608px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY7R5QFULtX1%2F3ss%2FcQEXXN4%3D" class="page" id="5" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-1-4" style="background-position: -464px -2624px;"></span>
    <span class="pdfImg-1-5" style="background-position: -1624px -3280px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY7R5QFULtX1%2F3ss%2FcQEXXN4%3D" class="page" id="6" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-3-4" style="background-position: -0px -0px;"></span>
    <span class="pdfImg-1-3" style="background-position: -232px -0px;"></span>
    <span class="pdfImg-2-6" style="background-position: -1624px -0px;"></span>
    <span class="pdfImg-5-9" style="background-position: -232px -328px;"></span>
    <span class="pdfImg-5-4" style="background-position: -696px -328px;"></span>
    <span class="pdfImg-3-2" style="background-position: -928px -328px;"></span>
    <span class="pdfImg-4-1" style="background-position: -2088px -328px;"></span>
    <span class="pdfImg-5-2" style="background-position: -1392px -656px;"></span>
    <span class="pdfImg-5-5" style="background-position: -1624px -656px;"></span>
    <span class="pdfImg-4-4" style="background-position: -1856px -656px;"></span>
    <span class="pdfImg-6-6" style="background-position: -464px -984px;"></span>
    <span class="pdfImg-7-5" style="background-position: -928px -984px;"></span>
    <span class="pdfImg-2-2" style="background-position: -1624px -984px;"></span>
    <span class="pdfImg-1-5" style="background-position: -0px -1312px;"></span>
    <span class="pdfImg-1-7" style="background-position: -696px -1312px;"></span>
    <span class="pdfImg-4-2" style="background-position: -1624px -1312px;"></span>
    <span class="pdfImg-5-3" style="background-position: -2088px -1312px;"></span>
    <span class="pdfImg-8-9" style="background-position: -0px -1640px;"></span>
    <span class="pdfImg-2-3" style="background-position: -232px -1640px;"></span>
    <span class="pdfImg-7-7" style="background-position: -464px -1640px;"></span>
    <span class="pdfImg-3-1" style="background-position: -928px -1640px;"></span>
    <span class="pdfImg-8-7" style="background-position: -2088px -1968px;"></span>
    <span class="pdfImg-4-6" style="background-position: -0px -2296px;"></span>
    <span class="pdfImg-6-1" style="background-position: -696px -2296px;"></span>
    <span class="pdfImg-6-7" style="background-position: -928px -2624px;"></span>
    <span class="pdfImg-3-3" style="background-position: -1160px -2624px;"></span>
    <span class="pdfImg-7-6" style="background-position: -1856px -2624px;"></span>
    <span class="pdfImg-6-3" style="background-position: -0px -2952px;"></span>
    <span class="pdfImg-2-7" style="background-position: -232px -2952px;"></span>
    <span class="pdfImg-7-3" style="background-position: -232px -3280px;"></span>
    <span class="pdfImg-3-7" style="background-position: -0px -3608px;"></span>
    <span class="pdfImg-4-7" style="background-position: -0px -3936px;"></span>
    <span class="pdfImg-1-6" style="background-position: -1160px -3936px;"></span>
    <span class="pdfImg-2-5" style="background-position: -232px -4264px;"></span>
    <span class="pdfImg-8-0" style="background-position: -696px -4264px;"></span>
    <span class="pdfImg-5-7" style="background-position: -928px -4264px;"></span>
    <span class="pdfImg-6-2" style="background-position: -1624px -4264px;"></span>
    <span class="pdfImg-7-2" style="background-position: -0px -4592px;"></span>
    <span class="pdfImg-3-6" style="background-position: -928px -4592px;"></span>
    <span class="pdfImg-8-6" style="background-position: -1624px -4592px;"></span>
    <span class="pdfImg-3-5" style="background-position: -1856px -4592px;"></span>
    <span class="pdfImg-7-0" style="background-position: -928px -4920px;"></span>
    <span class="pdfImg-1-2" style="background-position: -1856px -4920px;"></span>
    <span class="pdfImg-4-3" style="background-position: -2088px -4920px;"></span>
    <span class="pdfImg-8-5" style="background-position: -0px -5248px;"></span>
    <span class="pdfImg-6-5" style="background-position: -464px -5248px;"></span>
    <span class="pdfImg-2-4" style="background-position: -928px -5248px;"></span>
    <span class="pdfImg-8-3" style="background-position: -1160px -5248px;"></span>
    <span class="pdfImg-5-1" style="background-position: -1856px -5248px;"></span>
    <span class="pdfImg-4-5" style="background-position: -696px -5576px;"></span>
    <span class="pdfImg-5-6" style="background-position: -928px -5576px;"></span>
    <span class="pdfImg-1-4" style="background-position: -232px -5904px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY7R5QFULtX1%2F3ss%2FcQEXXN4%3D" class="page" id="7" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-5-1" style="background-position: -464px -0px;"></span>
    <span class="pdfImg-6-6" style="background-position: -928px -0px;"></span>
    <span class="pdfImg-2-1" style="background-position: -1856px -0px;"></span>
    <span class="pdfImg-5-8" style="background-position: -2088px -0px;"></span>
    <span class="pdfImg-4-5" style="background-position: -0px -328px;"></span>
    <span class="pdfImg-3-3" style="background-position: -1160px -328px;"></span>
    <span class="pdfImg-3-1" style="background-position: -1624px -328px;"></span>
    <span class="pdfImg-7-7" style="background-position: -0px -656px;"></span>
    <span class="pdfImg-7-3" style="background-position: -464px -656px;"></span>
    <span class="pdfImg-4-1" style="background-position: -928px -656px;"></span>
    <span class="pdfImg-1-3" style="background-position: -1160px -656px;"></span>
    <span class="pdfImg-3-4" style="background-position: -0px -984px;"></span>
    <span class="pdfImg-2-8" style="background-position: -232px -984px;"></span>
    <span class="pdfImg-4-7" style="background-position: -1160px -984px;"></span>
    <span class="pdfImg-1-4" style="background-position: -464px -1312px;"></span>
    <span class="pdfImg-8-2" style="background-position: -928px -1312px;"></span>
    <span class="pdfImg-8-3" style="background-position: -1856px -1312px;"></span>
    <span class="pdfImg-7-6" style="background-position: -1160px -1640px;"></span>
    <span class="pdfImg-3-8" style="background-position: -1392px -1640px;"></span>
    <span class="pdfImg-4-2" style="background-position: -1624px -1640px;"></span>
    <span class="pdfImg-2-7" style="background-position: -696px -1968px;"></span>
    <span class="pdfImg-5-3" style="background-position: -1160px -1968px;"></span>
    <span class="pdfImg-4-3" style="background-position: -1624px -1968px;"></span>
    <span class="pdfImg-1-6" style="background-position: -232px -2296px;"></span>
    <span class="pdfImg-6-1" style="background-position: -464px -2296px;"></span>
    <span class="pdfImg-1-5" style="background-position: -928px -2296px;"></span>
    <span class="pdfImg-5-5" style="background-position: -1160px -2296px;"></span>
    <span class="pdfImg-2-6" style="background-position: -1392px -2296px;"></span>
    <span class="pdfImg-4-4" style="background-position: -0px -2624px;"></span>
    <span class="pdfImg-1-9" style="background-position: -696px -2624px;"></span>
    <span class="pdfImg-4-8" style="background-position: -1160px -2952px;"></span>
    <span class="pdfImg-1-1" style="background-position: -1392px -2952px;"></span>
    <span class="pdfImg-3-6" style="background-position: -2088px -2952px;"></span>
    <span class="pdfImg-2-9" style="background-position: -0px -3280px;"></span>
    <span class="pdfImg-2-5" style="background-position: -464px -3280px;"></span>
    <span class="pdfImg-5-6" style="background-position: -928px -3280px;"></span>
    <span class="pdfImg-5-2" style="background-position: -1160px -3280px;"></span>
    <span class="pdfImg-3-2" style="background-position: -1392px -3280px;"></span>
    <span class="pdfImg-2-2" style="background-position: -2088px -3280px;"></span>
    <span class="pdfImg-2-4" style="background-position: -696px -3608px;"></span>
    <span class="pdfImg-3-7" style="background-position: -1160px -3608px;"></span>
    <span class="pdfImg-6-2" style="background-position: -2088px -3608px;"></span>
    <span class="pdfImg-5-4" style="background-position: -696px -3936px;"></span>
    <span class="pdfImg-2-3" style="background-position: -928px -3936px;"></span>
    <span class="pdfImg-7-8" style="background-position: -1856px -3936px;"></span>
    <span class="pdfImg-7-1" style="background-position: -2088px -3936px;"></span>
    <span class="pdfImg-5-9" style="background-position: -0px -4264px;"></span>
    <span class="pdfImg-8-1" style="background-position: -464px -4264px;"></span>
    <span class="pdfImg-6-7" style="background-position: -1160px -4264px;"></span>
    <span class="pdfImg-0-4" style="background-position: -2088px -4264px;"></span>
    <span class="pdfImg-4-6" style="background-position: -232px -4592px;"></span>
    <span class="pdfImg-7-9" style="background-position: -464px -4592px;"></span>
    <span class="pdfImg-1-7" style="background-position: -696px -4592px;"></span>
    <span class="pdfImg-7-2" style="background-position: -1160px -4592px;"></span>
    <span class="pdfImg-8-6" style="background-position: -2088px -4592px;"></span>
    <span class="pdfImg-4-9" style="background-position: -232px -4920px;"></span>
    <span class="pdfImg-1-2" style="background-position: -696px -4920px;"></span>
    <span class="pdfImg-3-9" style="background-position: -1160px -4920px;"></span>
    <span class="pdfImg-1-0" style="background-position: -1392px -4920px;"></span>
    <span class="pdfImg-6-9" style="background-position: -232px -5248px;"></span>
    <span class="pdfImg-6-8" style="background-position: -1624px -5248px;"></span>
    <span class="pdfImg-1-8" style="background-position: -0px -5576px;"></span>
    <span class="pdfImg-5-7" style="background-position: -1160px -5576px;"></span>
    <span class="pdfImg-6-3" style="background-position: -1392px -5576px;"></span>
    <span class="pdfImg-6-4" style="background-position: -2088px -5576px;"></span>
    <span class="pdfImg-2-0" style="background-position: -696px -5904px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY7R5QFULtX1%2F3ss%2FcQEXXN4%3D" class="page" id="8" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-4-4" style="background-position: -696px -0px;"></span>
    <span class="pdfImg-8-5" style="background-position: -1160px -0px;"></span>
    <span class="pdfImg-7-1" style="background-position: -1392px -0px;"></span>
    <span class="pdfImg-8-3" style="background-position: -464px -328px;"></span>
    <span class="pdfImg-3-2" style="background-position: -1392px -328px;"></span>
    <span class="pdfImg-6-8" style="background-position: -1856px -328px;"></span>
    <span class="pdfImg-7-6" style="background-position: -232px -656px;"></span>
    <span class="pdfImg-6-1" style="background-position: -696px -656px;"></span>
    <span class="pdfImg-1-7" style="background-position: -2088px -656px;"></span>
    <span class="pdfImg-5-3" style="background-position: -696px -984px;"></span>
    <span class="pdfImg-2-8" style="background-position: -1392px -984px;"></span>
    <span class="pdfImg-8-0" style="background-position: -1856px -984px;"></span>
    <span class="pdfImg-5-5" style="background-position: -2088px -984px;"></span>
    <span class="pdfImg-2-6" style="background-position: -232px -1312px;"></span>
    <span class="pdfImg-3-7" style="background-position: -1160px -1312px;"></span>
    <span class="pdfImg-1-6" style="background-position: -1392px -1312px;"></span>
    <span class="pdfImg-4-2" style="background-position: -696px -1640px;"></span>
    <span class="pdfImg-5-6" style="background-position: -1856px -1640px;"></span>
    <span class="pdfImg-6-5" style="background-position: -2088px -1640px;"></span>
    <span class="pdfImg-2-4" style="background-position: -0px -1968px;"></span>
    <span class="pdfImg-8-7" style="background-position: -232px -1968px;"></span>
    <span class="pdfImg-6-7" style="background-position: -464px -1968px;"></span>
    <span class="pdfImg-6-6" style="background-position: -928px -1968px;"></span>
    <span class="pdfImg-4-1" style="background-position: -1392px -1968px;"></span>
    <span class="pdfImg-3-5" style="background-position: -1856px -1968px;"></span>
    <span class="pdfImg-8-9" style="background-position: -1624px -2296px;"></span>
    <span class="pdfImg-3-3" style="background-position: -1856px -2296px;"></span>
    <span class="pdfImg-4-6" style="background-position: -2088px -2296px;"></span>
    <span class="pdfImg-3-1" style="background-position: -232px -2624px;"></span>
    <span class="pdfImg-4-7" style="background-position: -1392px -2624px;"></span>
    <span class="pdfImg-8-2" style="background-position: -1624px -2624px;"></span>
    <span class="pdfImg-2-7" style="background-position: -2088px -2624px;"></span>
    <span class="pdfImg-3-8" style="background-position: -464px -2952px;"></span>
    <span class="pdfImg-1-3" style="background-position: -696px -2952px;"></span>
    <span class="pdfImg-6-3" style="background-position: -928px -2952px;"></span>
    <span class="pdfImg-2-3" style="background-position: -1624px -2952px;"></span>
    <span class="pdfImg-7-3" style="background-position: -1856px -2952px;"></span>
    <span class="pdfImg-4-3" style="background-position: -696px -3280px;"></span>
    <span class="pdfImg-7-0" style="background-position: -1856px -3280px;"></span>
    <span class="pdfImg-4-5" style="background-position: -232px -3608px;"></span>
    <span class="pdfImg-2-1" style="background-position: -464px -3608px;"></span>
    <span class="pdfImg-1-8" style="background-position: -928px -3608px;"></span>
    <span class="pdfImg-1-4" style="background-position: -1392px -3608px;"></span>
    <span class="pdfImg-1-5" style="background-position: -1624px -3608px;"></span>
    <span class="pdfImg-2-5" style="background-position: -1856px -3608px;"></span>
    <span class="pdfImg-7-7" style="background-position: -232px -3936px;"></span>
    <span class="pdfImg-3-6" style="background-position: -464px -3936px;"></span>
    <span class="pdfImg-5-8" style="background-position: -1392px -3936px;"></span>
    <span class="pdfImg-8-8" style="background-position: -1624px -3936px;"></span>
    <span class="pdfImg-7-8" style="background-position: -1392px -4264px;"></span>
    <span class="pdfImg-4-8" style="background-position: -1856px -4264px;"></span>
    <span class="pdfImg-6-2" style="background-position: -1392px -4592px;"></span>
    <span class="pdfImg-0-8" style="background-position: -0px -4920px;"></span>
    <span class="pdfImg-1-1" style="background-position: -464px -4920px;"></span>
    <span class="pdfImg-8-6" style="background-position: -1624px -4920px;"></span>
    <span class="pdfImg-5-1" style="background-position: -696px -5248px;"></span>
    <span class="pdfImg-5-7" style="background-position: -1392px -5248px;"></span>
    <span class="pdfImg-3-4" style="background-position: -2088px -5248px;"></span>
    <span class="pdfImg-2-2" style="background-position: -232px -5576px;"></span>
    <span class="pdfImg-8-1" style="background-position: -464px -5576px;"></span>
    <span class="pdfImg-1-2" style="background-position: -1624px -5576px;"></span>
    <span class="pdfImg-5-2" style="background-position: -1856px -5576px;"></span>
    <span class="pdfImg-7-2" style="background-position: -0px -5904px;"></span>
    <span class="pdfImg-7-5" style="background-position: -464px -5904px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY9AFSQKeXLM5vwU4IJeyBRg%3D" class="page" id="9" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-4-4" style="background-position: -0px -0px;"></span>
    <span class="pdfImg-8-4" style="background-position: -232px -0px;"></span>
    <span class="pdfImg-7-8" style="background-position: -464px -0px;"></span>
    <span class="pdfImg-4-3" style="background-position: -1160px -0px;"></span>
    <span class="pdfImg-3-3" style="background-position: -0px -328px;"></span>
    <span class="pdfImg-1-9" style="background-position: -232px -328px;"></span>
    <span class="pdfImg-2-1" style="background-position: -464px -328px;"></span>
    <span class="pdfImg-5-6" style="background-position: -696px -328px;"></span>
    <span class="pdfImg-7-2" style="background-position: -928px -328px;"></span>
    <span class="pdfImg-3-1" style="background-position: -1624px -328px;"></span>
    <span class="pdfImg-2-0" style="background-position: -1856px -328px;"></span>
    <span class="pdfImg-1-3" style="background-position: -2088px -328px;"></span>
    <span class="pdfImg-2-4" style="background-position: -232px -656px;"></span>
    <span class="pdfImg-2-2" style="background-position: -928px -656px;"></span>
    <span class="pdfImg-6-3" style="background-position: -1624px -656px;"></span>
    <span class="pdfImg-8-6" style="background-position: -1856px -656px;"></span>
    <span class="pdfImg-2-3" style="background-position: -2088px -656px;"></span>
    <span class="pdfImg-3-6" style="background-position: -0px -984px;"></span>
    <span class="pdfImg-5-8" style="background-position: -696px -984px;"></span>
    <span class="pdfImg-6-8" style="background-position: -928px -984px;"></span>
    <span class="pdfImg-4-1" style="background-position: -1392px -984px;"></span>
    <span class="pdfImg-4-6" style="background-position: -1856px -984px;"></span>
    <span class="pdfImg-2-6" style="background-position: -2088px -984px;"></span>
    <span class="pdfImg-6-6" style="background-position: -464px -1312px;"></span>
    <span class="pdfImg-4-9" style="background-position: -928px -1312px;"></span>
    <span class="pdfImg-4-8" style="background-position: -1160px -1312px;"></span>
    <span class="pdfImg-5-9" style="background-position: -1856px -1312px;"></span>
    <span class="pdfImg-3-4" style="background-position: -2088px -1312px;"></span>
    <span class="pdfImg-3-2" style="background-position: -0px -1640px;"></span>
    <span class="pdfImg-7-7" style="background-position: -232px -1640px;"></span>
    <span class="pdfImg-8-8" style="background-position: -928px -1640px;"></span>
    <span class="pdfImg-2-5" style="background-position: -1392px -1640px;"></span>
    <span class="pdfImg-6-5" style="background-position: -1624px -1640px;"></span>
    <span class="pdfImg-8-7" style="background-position: -1856px -1640px;"></span>
    <span class="pdfImg-5-1" style="background-position: -2088px -1640px;"></span>
    <span class="pdfImg-3-5" style="background-position: -0px -1968px;"></span>
    <span class="pdfImg-6-2" style="background-position: -464px -1968px;"></span>
    <span class="pdfImg-6-7" style="background-position: -696px -1968px;"></span>
    <span class="pdfImg-6-9" style="background-position: -1624px -1968px;"></span>
    <span class="pdfImg-1-5" style="background-position: -2088px -1968px;"></span>
    <span class="pdfImg-6-4" style="background-position: -0px -2296px;"></span>
    <span class="pdfImg-4-5" style="background-position: -464px -2296px;"></span>
    <span class="pdfImg-8-2" style="background-position: -1160px -2296px;"></span>
    <span class="pdfImg-5-2" style="background-position: -1392px -2296px;"></span>
    <span class="pdfImg-7-5" style="background-position: -1624px -2296px;"></span>
    <span class="pdfImg-4-7" style="background-position: -1856px -2296px;"></span>
    <span class="pdfImg-1-0" style="background-position: -232px -2624px;"></span>
    <span class="pdfImg-3-7" style="background-position: -1392px -2624px;"></span>
    <span class="pdfImg-5-5" style="background-position: -1624px -2624px;"></span>
    <span class="pdfImg-7-6" style="background-position: -1856px -2624px;"></span>
    <span class="pdfImg-1-2" style="background-position: -0px -2952px;"></span>
    <span class="pdfImg-1-8" style="background-position: -464px -2952px;"></span>
    <span class="pdfImg-2-8" style="background-position: -696px -2952px;"></span>
    <span class="pdfImg-2-9" style="background-position: -928px -2952px;"></span>
    <span class="pdfImg-1-6" style="background-position: -1160px -2952px;"></span>
    <span class="pdfImg-7-4" style="background-position: -1624px -2952px;"></span>
    <span class="pdfImg-5-3" style="background-position: -1856px -2952px;"></span>
    <span class="pdfImg-4-2" style="background-position: -2088px -2952px;"></span>
    <span class="pdfImg-1-4" style="background-position: -0px -3280px;"></span>
    <span class="pdfImg-1-7" style="background-position: -232px -3280px;"></span>
    <span class="pdfImg-5-7" style="background-position: -696px -3280px;"></span>
    <span class="pdfImg-2-7" style="background-position: -928px -3280px;"></span>
    <span class="pdfImg-1-1" style="background-position: -1160px -3280px;"></span>
    <span class="pdfImg-8-5" style="background-position: -1392px -3280px;"></span>
    <span class="pdfImg-5-4" style="background-position: -1624px -3280px;"></span>
    <span class="pdfImg-3-8" style="background-position: -1856px -3280px;"></span>
    <span class="pdfImg-3-9" style="background-position: -0px -3608px;"></span>
    </div>
    <div bg="viewGbImg?fileName=oIeGseI4rxFumIG36taeY9AFSQKeXLM5vwU4IJeyBRg%3D" class="page" id="10" style="width:2315px;height:3274px;margin-left:-1157.5px;">
    <span class="pdfImg-3-5" style="background-position: -696px -0px;"></span>
    <span class="pdfImg-7-3" style="background-position: -928px -0px;"></span>
    <span class="pdfImg-3-2" style="background-position: -1392px -0px;"></span>
    <span class="pdfImg-6-5" style="background-position: -1624px -0px;"></span>
    <span class="pdfImg-1-2" style="background-position: -1856px -0px;"></span>
    <span class="pdfImg-3-3" style="background-position: -2088px -0px;"></span>
    <span class="pdfImg-1-4" style="background-position: -1160px -328px;"></span>
    <span class="pdfImg-4-2" style="background-position: -1392px -328px;"></span>
    <span class="pdfImg-1-3" style="background-position: -0px -656px;"></span>
    <span class="pdfImg-2-1" style="background-position: -464px -656px;"></span>
    <span class="pdfImg-2-4" style="background-position: -696px -656px;"></span>
    <span class="pdfImg-7-1" style="background-position: -1160px -656px;"></span>
    <span class="pdfImg-6-1" style="background-position: -1392px -656px;"></span>
    <span class="pdfImg-5-5" style="background-position: -232px -984px;"></span>
    <span class="pdfImg-1-1" style="background-position: -464px -984px;"></span>
    <span class="pdfImg-6-2" style="background-position: -1160px -984px;"></span>
    <span class="pdfImg-5-6" style="background-position: -1624px -984px;"></span>
    <span class="pdfImg-5-1" style="background-position: -0px -1312px;"></span>
    <span class="pdfImg-8-3" style="background-position: -232px -1312px;"></span>
    <span class="pdfImg-4-1" style="background-position: -696px -1312px;"></span>
    <span class="pdfImg-2-5" style="background-position: -1392px -1312px;"></span>
    <span class="pdfImg-3-4" style="background-position: -1624px -1312px;"></span>
    <span class="pdfImg-5-3" style="background-position: -464px -1640px;"></span>
    <span class="pdfImg-2-2" style="background-position: -696px -1640px;"></span>
    <span class="pdfImg-8-2" style="background-position: -1160px -1640px;"></span>
    <span class="pdfImg-8-0" style="background-position: -232px -1968px;"></span>
    <span class="pdfImg-4-3" style="background-position: -928px -1968px;"></span>
    <span class="pdfImg-7-4" style="background-position: -1160px -1968px;"></span>
    <span class="pdfImg-1-5" style="background-position: -1392px -1968px;"></span>
    <span class="pdfImg-7-2" style="background-position: -1856px -1968px;"></span>
    <span class="pdfImg-2-3" style="background-position: -232px -2296px;"></span>
    <span class="pdfImg-8-9" style="background-position: -696px -2296px;"></span>
    <span class="pdfImg-4-5" style="background-position: -928px -2296px;"></span>
    <span class="pdfImg-6-4" style="background-position: -2088px -2296px;"></span>
    <span class="pdfImg-4-6" style="background-position: -0px -2624px;"></span>
    <span class="pdfImg-7-0" style="background-position: -464px -2624px;"></span>
    <span class="pdfImg-3-1" style="background-position: -696px -2624px;"></span>
    <span class="pdfImg-1-6" style="background-position: -928px -2624px;"></span>
    <span class="pdfImg-5-4" style="background-position: -1160px -2624px;"></span>
    <span class="pdfImg-6-6" style="background-position: -2088px -2624px;"></span>
    <span class="pdfImg-5-2" style="background-position: -232px -2952px;"></span>
    <span class="pdfImg-7-5" style="background-position: -1392px -2952px;"></span>
    <span class="pdfImg-6-3" style="background-position: -464px -3280px;"></span>
    <span class="pdfImg-4-4" style="background-position: -2088px -3280px;"></span>
    </div>
    </div>
    '''

    last_page_id = process_file(html_source)
    print(last_page_id)
