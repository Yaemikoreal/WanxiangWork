# coding:utf-8
import re
from os import remove

from lxml.html import fromstring
from lxml import html, etree
import requests
from bs4 import BeautifulSoup,NavigableString
from botpy import logging
from lxml import html
from lxml.etree import tostring

_log = logging.get_logger()


class clear_spider:
    def __init__(self, **kwargs):
        self.html_all= kwargs.get('html')
        self.title=kwargs.get('title')

    def style_content(self,outerhtml):     #处理style标签，但不包括table
        root = html.fromstring(outerhtml)
        # 需要保留的样式
        allowed_styles = {"text-align:right", "text-align:center", "text-align: right", 'text-align: center'}

        # 处理所有带有style属性的标签，但不包括table标签
        for element in root.xpath('.//*[@style][not(ancestor::table)]'):
            # 获取当前元素的style属性值
            style_attr = element.get('style')

            # 拆分样式属性为多个键值对
            styles = [s.strip() for s in style_attr.split(';') if s]

            # 只保留允许的样式
            filtered_styles = [s for s in styles if any(allowed in s for allowed in allowed_styles)]

            # 重新构建style属性值
            new_style = '; '.join(filtered_styles)

            # 如果过滤后没有任何样式，则移除style属性
            if not new_style:
                element.attrib.pop('style', None)
            else:
                element.set('style', new_style)
        # 输出修改后的HTML
        return html.tostring(root, encoding='unicode')





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
        div_element = root.xpath('//div[@class="c-txt left"]')

        if div_element:
            # 获取特定div元素内部的所有内容
            div_content = div_element[0]

            # 将div内容转换为HTML字符串
            div_html = tostring(div_content, encoding='unicode')
            return div_html
        else:
            # 如果没有找到特定的div元素，返回None或适当的提示信息
            return None

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
        _log.info('-----------------------------------------------------------------------开始清洗%s', self.title)
        cleaning_failed = False


        try:
            outerhtml = self.out_html(self.html_all)  # 先拿到正文
        except Exception as e:
            _log.error("在获取正文时出错: %s", str(e))
            cleaning_failed = True

        if not cleaning_failed:
            try:
                style_html = self.style_content(outerhtml)  # 处理style标签，但不包括table
            except Exception as e:
                _log.error("在处理style标签时出错: %s", str(e))
                cleaning_failed = True

        if not cleaning_failed:
            try:
                script_html = self.script_content(style_html)  # 处理script标签

            except Exception as e:
                _log.error("在处理script标签时出错: %s", str(e))
                cleaning_failed = True

        if not cleaning_failed:
            try:
                table_clear_html = self.table_clear_content(script_html)  #

            except Exception as e:
                _log.error("在处理table标签时出错: %s", str(e))
                cleaning_failed = True

        if not cleaning_failed:
            try:
                space_clear_html = self.space_clear(table_clear_html)  # 处理空格
            except Exception as e:
                _log.error("在处理空格时出错: %s", str(e))
                cleaning_failed = True

        if cleaning_failed:
            # 如果在任何步骤中清洗失败，则标记清洗失败，并返回一个特殊的标识符
            space_clear_html = "<CLEANING_FAILED>"

        return space_clear_html



def main_test(data_dt=None):
    if data_dt is None:
        data_dt = {}
    obj = clear_spider(**data_dt)
    space_clear_html = obj.calculate()
    return  space_clear_html

if __name__ == '__main__':
    main_test()


