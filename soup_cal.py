from bs4 import BeautifulSoup, Comment
import re

"""
soup处理通用代码
"""
def _remove_attrs(soup):
    tds = """{text}"""
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))

    [comment.extract() for comment in comments]

    [s.extract() for s in soup('object')]
    # 清理文本内容
    a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
    b = re.compile("'")
    c = re.compile("\?")
    soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
    soup = BeautifulSoup(b.sub('', str(soup)), "html.parser")
    soup = BeautifulSoup(c.sub('', str(soup)), "html.parser")
    # 移除HTML注释和特定标签
    [s.extract() for s in soup('iframe')]
    [s.extract() for s in soup('video')]
    [s.extract() for s in soup('source')]
    [s.extract() for s in soup('source')]
    [s.extract() for s in soup('script')]
    [s.extract() for s in soup('style')]
    [s.extract() for s in soup('colgroup')]
    [s.extract() for s in soup('o:p')]
    [s.extract() for s in soup('w')]
    [s.extract() for s in soup('div', class_="video")]
    [s.extract() for s in soup('div', class_="fontsize")]

    # for test in soup.find_all('a',
    #                           href=re.compile('.*?(?!(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz))+$')):
    #     test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    #
    # for test in soup.find_all('a', href=re.compile('.htm')):
    #     test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    # 替换特定标签的内容
    for test in soup.find_all('b'):
        test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    for test in soup.find_all('strong'):
        test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    for test in soup.find_all('font'):
        test.attrs = {}
    # for test in soup.find_all('td'):
    #     test.attrs = {}
    for test in soup.find_all('li'):
        test.attrs = {}
    # for test in soup.find_all('tr'):
    #     test.attrs = {}
    for test in soup.find_all('br'):
        test.attrs = {}
    cc1 = re.compile(r'TEXT-ALIGN: right', re.I)
    cc2 = re.compile(r'text-align:right', re.I)
    cc3 = re.compile(r'text-align: right', re.I)
    cc4 = re.compile(r'TEXT-ALIGN:right', re.I)
    cc5 = re.compile(r'TEXT-ALIGN: center|text-align: center|TEXT-ALIGN:center|text-align:center', re.I)
    cc6 = re.compile(r'TEXT-ALIGN: left|text-align: left|TEXT-ALIGN:left|text-align:left|', re.I)
    for test in soup.find_all('p'):
        if test.get('align') == "center":
            test.attrs = {"align": "center"}
        elif test.get('align') == "right":
            test.attrs = {"align": "right"}
        elif test.get('align') == "left":
            test.attrs = {"align": "left"}
        elif test.get('style') is None:
            test.attrs = {}
        elif cc1.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc2.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc3.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc4.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc5.findall(test.get('style')):
            test.attrs = {"style": "text-align:center"}
        elif cc6.findall(test.get('style')):
            test.attrs = {"style": "text-align:left"}
        else:
            test.attrs = {}
    # 清除标签属性
    for test in soup.find_all('span'):
        test.attrs = {}
    for test in soup.find_all('table'):
        test.attrs = {"border": "1", "cellspacing": "0", "align": "center", "style": "width: 100%;"}
    for test in soup.find_all('li'):
        test.attrs = {"style": "list-style-type:none;"}
    # 处理段落样式
    dd1 = re.compile(r'text-align:center', re.I)
    dd4 = re.compile(r'text-align: center', re.I)
    dd2 = re.compile(r'text-align:right', re.I)
    dd3 = re.compile(r'text-align: right', re.I)
    for test in soup.find_all('div'):
        if test.get('style') is None:
            test.attrs = {}
        elif dd1.findall(test.get('style')):
            test.attrs = {"style": "text-align:center"}
        elif dd4.findall(test.get('style')):
            test.attrs = {"style": "text-align:center"}
        elif dd2.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif dd3.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif test.get('align') == "center":
            test.attrs = {"align": "center"}
        elif test.get('align') == "right":
            test.attrs = {"align": "right"}
        else:
            test.attrs = {}
    return soup