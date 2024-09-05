from bs4 import BeautifulSoup


def set_right_alignment(html_content):
    """
    本函数用于检查 HTML 中的标签，如果标签内的文本长度不超过 20 个字符，
    并且包含关键字之一，并且不包含排除字符串之一，则将这些标签的样式设置为靠右对齐。

    :param html_content: HTML 内容字符串
    :return: 修改后的 HTML 内容字符串
    """
    # 关键字列表
    keywords = ['海关', '局', '会', '年', '月', '日']

    # 排除字符串列表
    exclude_strings = ['条', '章', '解释', '指引', '服务']

    # 将 HTML 字符串解析为 BeautifulSoup 对象
    soup = BeautifulSoup(html_content, 'html.parser')

    # 遍历所有 <p> 标签
    for tag in soup.find_all('p'):
        # 获取标签的文本内容
        text = tag.get_text(strip=True)

        # 检查文本长度是否不超过 20 个字符
        if len(text) <= 20:
            # 检查文本是否包含关键字之一
            if any(keyword in text for keyword in keywords):
                # 检查文本是否包含排除字符串之一
                if not any(exclude_string in text for exclude_string in exclude_strings):
                    # 设置样式为靠右对齐
                    tag['style'] = 'text-align: right;'

    # 返回修改后的 HTML 内容
    return str(soup)


if __name__ == '__main__':
    # 示例 HTML 内容
    html_content = '<p>八、本通知自二〇〇九年一月一日起执行。</p>'

    # 调用函数并打印修改后的 HTML
    modified_html = set_right_alignment(html_content)
    print(modified_html)