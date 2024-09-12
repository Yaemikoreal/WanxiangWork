# coding:utf-8
import re
from os import remove

from lxml.html import fromstring
from lxml import html, etree
import requests
from bs4 import BeautifulSoup,NavigableString

class clear_spider:
    def __init__(self, html):
        self.html_all= html

    def style_content(self,outerhtml):     #处理style标签，但不包括table
        root = html.fromstring(outerhtml)
        # 需要保留的样式
        allowed_styles = {"text-align:right", "text-align:center", "text-align: right", 'text-align: center'}

        # 处理所有带有style属性的标签，但不包括table标签
        for element in root.xpath('//*/@style[not(ancestor::table)]'):
            # 获取父元素
            parent = element.getparent()
            style_attr = element
            new_style = '; '.join([s for s in style_attr.split(';') if any(allowed in s for allowed in allowed_styles)])

            if new_style:
                parent.set('style', new_style.strip())
            else:
                parent.attrib.pop('style', None)

        # 将修改后的HTML转换回字符串
        cleaned_html = html.tostring(root, encoding='unicode')
        return cleaned_html

    #处理script标签格式问题
    def script_content(self,script_html):
        remove_lt = ['script']
        soup = BeautifulSoup(script_html,"html.parser")
        for rm_it in remove_lt:
            for tag in soup.find_all(rm_it):
                # DEL
                tag.decompose()
        script_html = str(soup)
        return script_html







    #处理表格部分
    def table_clear_content(self,cleaned_html):
        pegex = re.findall(r'(<table.*?</table>)', cleaned_html, re.DOTALL)
        for i in pegex:
            table_name=i.replace('<p style="text-indent:2em;">','<p>')
            cleaned_html=cleaned_html.replace(i,table_name)
        clear_html_new=re.findall('<table.*?>',cleaned_html)
        for t in clear_html_new:
            cleaned_html=cleaned_html.replace(t,'<table align="center" border="1" cellspacing="0" style="width:100%">').replace('&nbsp; ','').replace('&nbsp;','')
        return cleaned_html

    #处理拿到正文
    def out_html(self,html_all):

        # 解析HTML字符串为ElementTree对象
        root = fromstring(html_all)

        # 使用XPath选择器来定位具有特定类名的div元素
        div_element = root.xpath('//div[@class="zcwjk-xlcon"]')

        # 输出找到的div元素
        if div_element:
           return etree.tostring(div_element[0], pretty_print=True).decode()

    #处理空格
    def space_clear(self,table_clear_html):
        soup = BeautifulSoup(str(table_clear_html), "html.parser")
        for tag in soup.find_all(True):
            if tag.string and isinstance(tag.string, NavigableString):
                # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
                # 将非换行空格替换为空格
                new_string = tag.string.replace(' ', " ")
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
        soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
        return soup

    def calculate(self,):
        """
        类方法总流程
        :return:
        """
        outerhtml=self.out_html(self.html_all)                      #先拿到正文
        style_html=self.style_content(outerhtml)                    #处理style标签，但不包括table
        script_html=self.script_content(style_html)                 #处理script标签
        table_clear_html=self.table_clear_content(script_html)      #处理table标签
        space_clear_html=self.space_clear(table_clear_html)         #处理空格
        return space_clear_html



def main_test(data_dt=None):
    if data_dt is None:
        data_dt = {}
    obj = clear_spider(data_dt.get("html"))
    space_clear_html = obj.calculate()
    return  space_clear_html

if __name__ == '__main__':
    main_test()


