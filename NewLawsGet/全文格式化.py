from bs4 import BeautifulSoup
import re


def deal_full(data):
    # 替换标题为p标签,替换div为P
    data = str(data).replace('div', 'p')
    data = str(data).replace('h1', '').replace('h2', '').replace('h3', '')
    # 过滤a标签里的name属性
    data = re.sub('<a.*?name.*?>', '<a>', data)
    data = re.sub('id=".*?"', '', data)
    data = data.replace('anchor="anchor"', '')
    return data


# 移除所有的字体，字号
def remove_font_styles(data):
    soup = BeautifulSoup(data, 'html.parser')
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


if __name__ == '__main__':
    with open('./格式处理.html', 'r', encoding='utf-8') as f:
        data = f.read()
        data = deal_full(data)
        data = remove_font_styles(data)
        print(data)
