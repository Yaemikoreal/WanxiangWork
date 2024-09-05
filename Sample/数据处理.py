# -*- coding: utf-8 -*-
import re
import time
import hashlib
from 去重 import lar_esquc,chl_esquc,check_existence,camptime,downfile,downfile_img,save_sql_BidDocument
from 预处理 import _remove_attrs
import requests
import pandas as pd
from functools import partial
import datetime
from multiprocessing.dummy import Pool
from bs4 import BeautifulSoup
import cchardet
import pyodbc
from 类别判断 import get_catagroy
from pyquery.pyquery import PyQuery as pq

def tihuan_full(str1):
    new_str = _remove_attrs(str1)
    for a in new_str:
        if '<p style="text-align:left">' in str(a):
            b = str(a).replace('<p style="text-align:left">','<p>')
            return b

class decide(object):
    def __init__(self):
        self.shouludate = str(datetime.date.today()).replace('-', '.')
        self.gjc=list(pd.read_excel(rf'C:\Users\小可爱\Downloads\不收录关键词.xlsx')['关键词'])
        self.main_url='https://zrzyt.qinghai.gov.cn/gk/zc/hzgfxwj_1'
        self.cookies = {'_trs_uv': 'lu80x8rg_246_czik','_trs_ua_s_1': 'lw1gv1pm_246_28ob'}
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37'}

    def get_sql_menus(self,key,menuname):
        '''获取数据库中指定的部门编号'''
        connect = pyodbc.connect(
            'Driver={SQL Server};Server=47.97.3.24,14333;Database=LawEnclosure;UID=saa;PWD=1+2-3..*Qwe!@#;'
            'charset=gbk')
        # print('数据库连接成功')
        # 创建游标对象
        cursor = connect.cursor()
        sql=f"SELECT [key],[value] FROM [FddLaw5.0].[dbo].[menus] WHERE [key] LIKE N'{key}%' AND [menuname] LIKE N'%{menuname}%' and parentid like '{key}%'"
        cursor.execute(sql)
        url_list = cursor.fetchall()
        department_dict = {text:code for code, text in url_list}
        return department_dict

    def split(self,str):
        if len(str) >= 10:
            new_str = str[0:10].replace('-', '.')
            return new_str
        else:
            new_str = str.replace('-', '.')
            return new_str

    def gettype(self,hrefnn):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        wy = requests.get(hrefnn, headers=self.headers, verify=False)
        wy.encoding = wy.apparent_encoding
        bs4wy = BeautifulSoup(wy.text, "html.parser")
        type = bs4wy.find('table', class_="govDetailTable")
        return type

    def ask(self,page):
        '''获取网页数据，并进行数据清洗'''
        if page==0:page_url=self.main_url
        else:page_url=self.main_url.replace('hzgfxwj_1',f'hzgfxwj_{page}')
        print(page_url)
        time.sleep(1)
        response = requests.get(page_url, cookies=self.cookies, headers=self.headers)
        response.encoding=cchardet.detect(response.content)['encoding']
        page_html_text=response.text
        soup=BeautifulSoup(page_html_text,'lxml')
        list_detail=soup.find('ul', class_='infoList').prettify()
        pyquerypq = pq(list_detail).find('li').items()
        for one_data in pyquerypq:
            title=one_data.find('a').text()#法规标题
            href = 'https://zrzyt.qinghai.gov.cn' + one_data.find('a').attr('href')  # 法规链接
            pagedate=self.split(one_data.find('span.date').text())#官网发布日期
            Issued_Number=self.gettype(href).find_all('tr')[2].find_all('td')[1].text#发文字号
            ddd = '青海'
            sss = lar_esquc(title, '标题')
            result_renshi = any(data in title for data in self.gjc)#人事任免信息
            if (sss or '公告' in title or '通报' in title or ('平台迁移' in title and '通知' in title) or '通告' in title or '公示' in title or title[-2:] == '总结' or title[-2:] == '年报' or title[-2:] == '管理' or title[-2:] == '报告' or '解读' in title or '答记者问' in title) and '...' not in title:
                pass
            else:
                def query(list_name, ddd1, ddd2):
                    query1 = {
                        "query": {"bool": {
                            "must": [{"match_phrase": {list_name: ddd1}},
                                     {"match_phrase": {list_name: ddd2}}]}}}
                    query2 = {"query": {"match": {list_name: ddd2}}}
                    return [query1, query2]
                chatitle = title
                query1 = query('标题', ddd, chatitle)[0]
                query2 = query('发文字号', ddd, Issued_Number)[1]
                a = check_existence(title, title, '标题', query1, '827')
                b = check_existence(Issued_Number, Issued_Number, '发文字号', query2, '827')
                if (lar_esquc(title, '标题') or a) and title[-3:] != '...':
                    pass
                else:
                    if (lar_esquc(Issued_Number,'发文字号') or b) and len(Issued_Number.strip())>2:
                        pass
                    else:
                        time.sleep(1)
                        times = time.time()
                        wybz = title
                        hash_object = hashlib.md5()
                        # 更新hash对象
                        hash_object.update(wybz.encode())
                        unique_sign = hash_object.hexdigest()#唯一标志
                        allimfomation=self.get_detail_page(href,title,pagedate)
                        Description=allimfomation[0]#全文
                        Release_date=allimfomation[1]#发布日期
                        Implementation_date=allimfomation[2]#实施日期
                        Timeliness=allimfomation[3]#时效性
                        departments=allimfomation[4]#发布部门
                        category=allimfomation[5]#类别
                        if result_renshi:
                            category = '088;08804'
                        effectiveness_level=allimfomation[6]#效力级别
                        data_one=[unique_sign,title,Description,departments,category,Release_date,effectiveness_level,Implementation_date,Issued_Number,Timeliness,href,self.shouludate]
                        # sql = rf"INSERT INTO [自收录数据].dbo.[专项补充收录_copy1] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES ('{unique_sign}','{title}','{Description}','{departments}','{category}','{Release_date}','{effectiveness_level}','{Implementation_date}','{Issued_Number}','{Timeliness}','{href}','{self.shouludate}')"
                        # save_sql_BidDocument(sql)
                        print(data_one)

    def center_title(self,Description,title):
        '''段中标题数据居中'''
        cha = re.findall('<p>(.*?)</p>', Description)
        for ii in cha:
            txzt = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', ii)
            zxt = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
            if len(txzt) > 1:
                if str(txzt) in str(zxt):
                    Description = Description.replace(f'<p>{ii}</p>', f'<p style="text-align:center;">{ii}</p>')
        return Description

    def starthello(self,Description):
        '''首行问候语段前不空格'''
        try:
            try:
                aaaa = re.findall('(<p>.*?：</p>)', Description)[0]
            except:
                aaaa = re.findall('(<p>.*?:</p>)', Description)[0]
            if aaaa in Description[:150]:
                zzzz1 = aaaa.replace('<p>','<p style="text-indent: 0em;text-align:left">')
                Description = Description.replace(aaaa, zzzz1)
        except:Description=Description
        return Description

    def get_date(self,Description,title,Timeline,pagedate):
        '''获取发布日期和实施日期'''
        dddd=Description.replace('&nbsp;','').replace(' ','')
        try:
            release_date=camptime(str(re.findall('>.{0,6}年.{0,3}月.{0,3}日</p>',dddd)[0][1:]).replace('</p>',''),"%Y年%m月%d日")
        except:
            release_date=pagedate
        if '转发' in title:
            Implementation_date=release_date
        else:
            texxt=pq(Description).text()
            ssfile = re.findall('本(.{0,5})自(.{0,6})年(.{0,3})月(.{0,3})日(起{0,1})', texxt)
            date_list = ''
            if len(ssfile) > 0:
                for y in range(len(ssfile[0])):
                    yy = ssfile[0][y]
                    if y == 0 or y == len(ssfile[0]) - 1:pass
                    else:
                        x = yy.replace('</span>', '').replace('<span>', '')
                        date_list += (x + '.')
                try:
                    Implementation_date = camptime(date_list.split('>')[-1], "%Y.%m.%d.")
                except:
                    Implementation_date = release_date
            else:
                Implementation_date = release_date
            if Implementation_date > self.shouludate:Timeline = '04'
            else:Timeline = Timeline
        return [release_date,Implementation_date,Timeline]

    def tupiangeshi(self,Description):
        '''设置图片格式'''
        ddd = re.findall('<img.*?>', Description)
        for dzz in ddd:
            ppp = re.findall('src="/datafolder.*?"', dzz)
            try:
                pppqqq = '<img style="max-width: 100%; display:block; margin:0 auto;" ' + ppp[0] + '/>'
                Description = Description.replace(dzz, pppqqq)
            except:
                Description=Description
        return Description

    def table_chuli(self,Description):
        '''设置表格格式，定义表格最大宽度为页面的100%并根据网页内容自行调整'''
        zzzz = re.findall('(<table.*?</table>)', Description)
        for i in zzzz:
            soup = BeautifulSoup(i, 'html.parser')
            # 找到所有的 <p> 标签并逐个处理
            for p_tag in soup.find_all('p'):
                p_tag.unwrap()  # 删除 <p> 标签，但保留其中的文本内容
            strs = soup.prettify()
            tab = strs.replace('    ', '').replace('   ', '').replace('   <', '<').replace('  <', '<').replace(' <','<').replace('\n', '')
            Description = Description.replace(i, tab)
        tttt = re.findall('(<table.*?>)', Description)
        for t in tttt:
            Description = Description.replace(t, '<table align="center" border="1" cellspacing="0" style="max-width:100%;width:auto;">').replace('&nbsp; ', '').replace('&nbsp;', '')
        return Description

    def department(self,Description,title,bumenall):
        '''匹配文中的发布部门'''
        fabubumen = ''
        text_bumen= pq(Description).find('p[style*="right"]').text() + pq(Description).find('p[align="right"]').text()
        bumena = text_bumen + title
        values = [str(bumenall[dept]) for dept in bumenall if dept in bumena]
        values = sorted(list(set(values)), key=len)
        fabubumen = ''
        for value in values:
            if '8' in str(values):
                if value == '8' or '8' not in value:
                    pass
                else:
                    fabubumen += ';' + value
        if ';' not in fabubumen[1:]:
            if len(fabubumen[1:]) == 5:
                fabubumen = fabubumen[1:2] + ';' + fabubumen[1:4] + ';' + fabubumen[1:6]
            else:
                fabubumen = fabubumen[1:2] + ';' + fabubumen[1:4] + ';' + fabubumen[
                                                                          1:6] + fabubumen
        else:
            if values[-1][:5] == values[-1]:
                fabubumen = fabubumen[1:].replace(values[-1], '').replace('827;',
                                                                          f'8;827;{values[-1][:5]}')
            else:
                fabubumen = fabubumen[1:].replace('82703;', f'8;827;{values[-1][:5]};')
        if fabubumen!=';;' and ';827;' not in fabubumen:
            fabubumen=fabubumen[0]+';'+fabubumen[:3]+';'+fabubumen[:5]+';'+fabubumen
        return fabubumen

    # def categorys(self):

    def get_detail_page(self,href,title,pagedate):
        '''网页数据清洗以及各项属性获取'''
        the_detail_response = requests.get(href, headers=self.headers,cookies=self.cookies)  # , proxies=self.proxies)
        the_detail_response.encoding = cchardet.detect(the_detail_response.content)['encoding']
        detail_html_text = the_detail_response.text
        soup = BeautifulSoup(str(detail_html_text), "html.parser")
        quanwen = soup.find('div', class_="conTxt")
        Description = str(_remove_attrs(quanwen)).encode('gbk', errors='ignore').decode('gbk')
        Timeline='01'
        effectiveness_level='XP10'#效力级别
        if '否' in pq(detail_html_text).find('#printStart1 > div:last-child > span[class="d3"]').text():
            Timeline='02'
        Description=Description.replace('</span>','').replace('<span>','')
        Description=self.center_title(Description,title)
        Description=self.starthello(Description)
        Release_date=self.get_date(Description,title,Timeline,pagedate)[0]#发布日期
        Implementation_date = self.get_date(Description,title,Timeline,pagedate)[1]#实施日期
        Timeliness=self.get_date(Description,title,Timeline,pagedate)[-1]#时效性
        Description=Description.replace('<p>','<p style="text-indent:2em;">')
        soup1 = BeautifulSoup(str(Description), "html.parser")
        Description=downfile(self.headers,self.cookies,href,soup1,Description)
        Description=self.table_chuli(self.tupiangeshi(downfile_img(self.headers,self.cookies,href,soup1,Description)))
        bumenall=self.get_sql_menus('827','lar_fdep_id')
        departments=self.department(Description,title,bumenall)#发布部门
        category='003;00301'#类别获取函数还未处理，需手动获取类别
        try:
            category = get_catagroy(title)
        except:
            category = category

        return [Description,Release_date,Implementation_date,Timeliness,departments,category,effectiveness_level]

    def run(self):
        url_list = list(range(5))
        partial_function = partial(self.ask)
        pool = Pool(4)
        pool.map(partial_function, url_list)

if __name__ == "__main__" :
    decide=decide()
    decide.run()