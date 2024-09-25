import os
import random
import time

from bs4 import BeautifulSoup, NavigableString
import re
from query import PublicFunction


def deal_full(data_str):
    """
    使用BeautifulSoup处理HTML文档，替换和过滤特定标签和属性。
    参数:
    data_str (str): 输入的HTML字符串。
    返回:
    str: 处理后的HTML字符串。
    """
    # 解析HTML文档
    soup = BeautifulSoup(data_str, 'html.parser')
    # 替换div标签为p标签
    for div_tag in soup.find_all('div'):
        div_tag.name = 'p'
    # 删除h1, h2, h3标签
    for tag_name in ['h1', 'h2', 'h3']:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    # 过滤a标签里的name属性
    for a_tag in soup.find_all('a'):
        if 'name' in a_tag.attrs:
            del a_tag['name']
        if 'id' in a_tag.attrs:
            del a_tag['id']
        if 'anchor' in a_tag.attrs:
            del a_tag['anchor']
    # 渲染修改后的HTML
    modified_html = str(soup)
    return modified_html


# 移除所有的字体，字号
def remove_font_styles(data_str):
    soup = BeautifulSoup(data_str, 'html.parser')
    # 移除头顶空格
    fulltext_tags = soup.find_all('p', class_='fulltext')

    # 遍历找到的标签
    for tag in fulltext_tags:
        # 把标签内容替换为标签内部的内容
        tag.unwrap()

    # 移除所有的 <font> 标签
    for font_tag in soup.find_all('font'):
        font_tag.unwrap()

    # 移除所有的 style 属性中的字体和字号样式
    for tag in soup.find_all(True):
        if 'style' in tag.attrs:
            styles = tag['style'].split(';')
            new_styles = [style for style in styles if not ('font-family' in style or 'font-size' in style)]
            if new_styles:
                tag['style'] = ';'.join(new_styles)
            else:
                del tag['style']
    # 移除无用的图标图片，给所有图片添加居中属性
    useless_icons = soup.find_all('img', style='vertical-align: middle; margin-right: 2px;')
    for icon in useless_icons:
        icon.decompose()
    # 找到所有的 img 标签
    img_tags = soup.find_all('img')

    # 遍历每一个 img 标签，并添加 居中 属性
    soup = str(soup)
    for img in img_tags:
        img['style'] = 'display: block; margin-left: auto; margin-right: auto;'
    # 替换talbe和td的第二种方法，替换关键词
    soup = soup.replace('<table ', '<table style="margin-left: auto; margin-right: auto;" ')

    # 把所有的span标签替换为p标签
    soup = re.sub('<span.*?>', '', soup)
    soup = re.sub('</span.*?>', '', soup)

    # 把nbsp替换为普通空格
    # soup = re.sub('&nbsp;', ' ', soup)

    # 替换所有的</p><br/>
    soup = soup.replace('</p><br/>', '</p>')

    return str(soup)


def changeinfo(html):
    # 检查html是否为None
    if html is not None:
        # 查找并移除包含"附件预览"的<div>标签
        for div_tag in html.find_all('div'):
            if '附件预览' in str(div_tag):
                div_tag.extract()

        # 处理所有的<a>标签
        for anchor in html.find_all('a'):
            anchor_text = str(anchor)

            # 移除包含特定字符串的<a>标签
            if 'vpn_inject_scripts' in anchor_text or 'tiao_' in anchor_text:
                anchor.extract()
                continue

            href = anchor.get('href')
            onmouseover = anchor.get('onmouseover')

            if onmouseover is None:
                continue

            # 提取onmouseover属性中的信息
            pattern = re.compile(r'AJI\((.*?)\)')
            match = re.search(pattern, onmouseover)
            if not match:
                continue

            right = match.group(1)
            right_values = right.split(',')

            if '/chl/' in str(href) or '/lar/' in str(href):
                rginfo = ''
                if len(right_values) >= 2:
                    for value in right_values:
                        rginfo += str(int(float(value))) + ','
                    rginfo = rginfo[:-1]
                else:
                    rginfo = right_values[0] + ',0'

                anchor.attrs = {
                    'href': f'javascript:SLC({rginfo})',
                    'onmouseover': f'javascript:AJI({rginfo})',
                    'class': 'alink'
                }
        # 移除特定的字体大小样式
        html = str(html).replace('font-size: 16px;', '')
        html = str(html).replace('font-size: 18px;', '')

    return html


def attachment_processing(soup):
    """
        附件和全文处理函数
        :return:
        """
    full = changeinfo(soup)
    full = BeautifulSoup(full, "html.parser")
    [s.extract() for s in full.find_all('button')]
    [s.extract() for s in full.find_all('small')]
    full = str(full).replace("附法律依据", '')
    full = str(full).replace("附：相关法律条文            ", '')
    full = str(full)
    b = re.compile(r"'")
    full = b.sub('', str(full))
    full = b.sub('窗体底端', str(full))
    full = b.sub('窗体顶端', str(full))
    full = full_calculate(full)

    return full


def remove_nbsp(soup):
    """
    对初步清洗的soup进行进步格式清洗
    :param soup: 初步清洗的soup
    :return: 最终结果
    """
    # 遍历所有的文本节点
    for tag in soup.find_all(True):
        if tag.string and isinstance(tag.string, NavigableString):
            # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
            # 将非换行空格替换为空格
            new_string = tag.string.replace(' ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(' ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace('  ', " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(" ", " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace("  ", " ")
            tag.string.replace_with(new_string)
            new_string = tag.string.replace(" ", " ")
            tag.string.replace_with(new_string)
    a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
    soup = BeautifulSoup(a.sub(' ', str(soup)), "html.parser")

    remove_text_lt = ['span', 'video', 'p']
    for it_t in remove_text_lt:
        # 遍历所有的对应标签
        for span in soup.find_all(it_t):
            # 如果对应标签的文本为空，则移除它
            if not span.get_text().strip():
                span.decompose()

    # 如果有抄送，删除抄送
    for it in soup.find_all('p'):
        tag_text = it.get_text()
        if "抄送" in tag_text:
            it.decompose()

    # 删除法宝新AI
    for it in soup.find_all('a', logfunc='法宝新AI'):
        it.decompose()
    # 删除本法变迁
    for it in soup.find_all('a', logfunc='本法变迁'):
        it.decompose()
    # 将 soup 转换为字符串
    html_str = str(soup)
    # 使用正则表达式移除 HTML 注释
    html_str_without_comments = re.sub(r'<!--(.*?)-->', '', html_str, flags=re.DOTALL)
    # 重新解析成一个新的 soup 对象
    soup = BeautifulSoup(html_str_without_comments, 'html.parser')
    return soup


def soup_cal(soup_ture):
    """
    传入正文部分soup，传出初步清洗的结果soup
    :param soup_ture:
    :return:
    """
    not_dt = {"text-align:right", "text-align:center", "text-align: right", 'text-align: center', 'id'}

    def process_style(tag_s):
        style = tag_s.get('style')
        if style:
            styles = [s.strip() for s in style.split(';') if s.strip()]
            new_styles = []
            for s in styles:
                # 如果样式是 text-align:end 或 text-align: end，则替换为 text-align:right
                if s.startswith('text-align:end') or s == 'text-align: end':
                    s = 'text-align:right'
                if s in not_dt or s.startswith('text-align:right'):
                    new_styles.append(s)

            if new_styles:
                tag_s['style'] = '; '.join(new_styles)
            else:
                del tag_s['style']

    for tag in soup_ture.find_all(True):
        attrs_to_remove = ['data-index', 'id', 'class', 'type', 'new', 'times', 'lang', 'clear', 'content',
                           'http-equiv', 'name', 'rel']
        for attr in attrs_to_remove:
            # tag.attrs 包含了标签的所有属性
            if attr in tag.attrs:
                del tag[attr]
        process_style(tag)
    # # 处理可能的顶级元素样式
    process_style(soup_ture)
    return soup_ture


def full_calculate(full):
    """
    原有全文处理函数
    :param full: 全文字符串
    :return:
    """
    full = deal_full(full)
    full = remove_font_styles(full)
    return full


def new_full_calculate(full):
    """
    全文内容二次格式修改
    :param full:
    :return:
    """
    full_soup = BeautifulSoup(full, "html.parser")
    full_soup = soup_cal(full_soup)
    full_soup = remove_nbsp(full_soup)
    full = str(full_soup)
    return full


def main_test():
    with open('../附件/test.txt', 'r', encoding='utf-8') as f:
        data = f.read()
        data_soup = BeautifulSoup(data, "html.parser")
        full = attachment_processing(data_soup)
        data = full_calculate(full)
        full = new_full_calculate(data)
        print(1)
        return full


if __name__ == '__main__':
    main_test()
