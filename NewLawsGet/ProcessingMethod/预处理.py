import re
import time

from bs4 import BeautifulSoup, Comment

from .链接数据库 import sql_server_info, get_connect_cursor, query, insert_, query_1, query_del


def _remove_attrs(soup):
    tds = """{text}"""
    comments = soup.findAll(text=lambda text: isinstance(text, Comment))

    [comment.extract() for comment in comments]

    [s.decompose() for s in soup('object')]
    a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
    b = re.compile("'")
    c = re.compile("\?")
    soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")
    soup = BeautifulSoup(b.sub('', str(soup)), "html.parser")
    soup = BeautifulSoup(c.sub('', str(soup)), "html.parser")

    [s.decompose() for s in soup('iframe')]
    [s.decompose() for s in soup('button')]
    [s.decompose() for s in soup('video')]
    [s.decompose() for s in soup('source')]
    [s.decompose() for s in soup('source')]
    [s.decompose() for s in soup('script')]
    [s.decompose() for s in soup('style')]
    [s.decompose() for s in soup('colgroup')]
    [s.decompose() for s in soup('o:p')]
    [s.decompose() for s in soup('w')]
    [s.decompose() for s in soup('div', class_="video")]

    [s.decompose() for s in soup('div', class_="fontsize")]

    for test in soup.find_all('a',
                              href=re.compile('.*?(?!(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz))+$"')):
        test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))

    for test in soup.find_all('a', href=re.compile('.htm')):
        test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    for test in soup.find_all('b'):
        test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    for test in soup.find_all('strong'):
        test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
    for test in soup.find_all('font'):
        test.attrs = {}
    for test in soup.find_all('td'):
        flag = True
        if test.get('rowspan'):
            test.attrs = {"rowspan": test.get('rowspan')}
            flag = False
        if test.get('colspan'):
            test.attrs = {"colspan": test.get('colspan')}
            flag = False
        if flag:
            test.attrs = {}
    for test in soup.find_all('li'):
        test.attrs = {}
    for test in soup.find_all('tr'):
        for test in test.find_all('tr'):
            flag=True
            if test.get('rowspan'):
                test.attrs={"rowspan":test.get('rowspan')}
                flag=False
            if test.get('colspan'):
                test.attrs={"colspan":test.get('colspan')}
                flag=False
            if  flag:
                test.attrs = {}
    for test in soup.find_all('br'):
        test.attrs = {}
    cc1 = re.compile(r'TEXT-ALIGN: right', re.I)
    cc2 = re.compile(r'text-align:right', re.I)
    cc3 = re.compile(r'text-align: right', re.I)
    cc4 = re.compile(r'TEXT-ALIGN:right', re.I)
    for test in soup.find_all('p'):
        if test.get('style') is None:
            test.attrs = {}
        elif cc1.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc2.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc3.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif cc4.findall(test.get('style')):
            test.attrs = {"style": "text-align:right"}
        elif test.get('align') == "center":
            test.attrs = {"align": "center"}
        elif test.get('align') == "right":
            test.attrs = {"align": "right"}
        else:
            test.attrs = {}

    for test in soup.find_all('span'):
        test.attrs = {}
    for test in soup.find_all('table'):
        test.attrs = {"border": "1", "cellspacing": "0", "align": "center", "style": "width: 100%;"}
    for test in soup.find_all('li'):
        test.attrs = {"style": "list-style-type:none;"}

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


def intaa(text):
    _size = re.findall(r'\d', str(text))
    numm = ''
    for ii in _size:
        numm = numm + ii
    if numm == '':
        return ''
    return int(numm)


def intDate(text):
    numm = ['', '', '']

    cc = 0
    date = ''
    text = text.replace("\n", '').replace("\t", '').replace(" ", '')
    text = text.replace('&nbsp;', '')
    text = text.replace(' ', '')
    for i in range(0, len(text)):
        if re.findall(r'\d', text[i]):
            numm[cc] = numm[cc] + text[i]
        else:
            cc += 1
    for nn in numm:
        if len(nn) < 2:
            nn = '0' + nn
        date += nn
    return int(date)


# cc="2020年4月17日"
# print(intDate(cc))
def insertsql(sql):
    conninfo = sql_server_info()
    #print(conninfo)
    connInfo = sql_server_info("服务器")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    insert_(connInfo, sql)

def insertsql_124(sql):
    conninfo = sql_server_info()
    #print(conninfo)
    connInfo = sql_server_info("124")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    insert_(connInfo, sql)

def selectsqls_124(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("124")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query_1(cursor, sql)
    # print(qu_rs)
    if qu_rs != None:
        return qu_rs
    else:
        return ""

def insertsql6(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("法宝6.0")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    insert_(connInfo, sql)


def selectsql6(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("法宝6.0")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query(cursor, sql)
    # print(qu_rs)
    if qu_rs == None:
        return True
    else:
        return False



def seletsql6time(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("法宝6.0")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query(cursor, sql)
    # print(qu_rs)
    if qu_rs != None:
        return qu_rs
    else:
        return ""



def seletsql5(sql):
    conninfo = sql_server_info()

    connInfo = sql_server_info("法宝5.0")
    connect_cursor = get_connect_cursor(connInfo)
    print(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    # qu_rs = query_1(cursor, sql)
    # # print(qu_rs)
    # if qu_rs != None:
    #     return qu_rs
    # else:
    #     return ""


def selectsql(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("服务器")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query(cursor, sql)
    # print(qu_rs)
    if qu_rs != None:
        return True
    else:
        return False


def selectsqls(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("服务器")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query_1(cursor, sql)
    # print(qu_rs)
    if qu_rs != None:
        return qu_rs
    else:
        return ""



def deletesql(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("服务器")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    query_del(connInfo, sql)


def deletesql_124(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("124")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    query_del(connInfo, sql)

def iscuncunzai(sql):
    conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("服务器")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query(cursor, sql)
    # print(qu_rs)
    if qu_rs != None:
        return False
    else:
        return True


def gettimestr():
    ct = time.time()
    timem = time.strftime('%Y%m%d%H%M%S', time.localtime(ct))
    data_secs = (ct - int(ct)) * 1000
    return timem + str(int(data_secs))


def iscuncunzaif(sql):
    # conninfo = sql_server_info()
    # print(conninfo)
    connInfo = sql_server_info("法宝6.0")
    connect_cursor = get_connect_cursor(connInfo)
    connect = connect_cursor[0]
    cursor = connect_cursor[1]
    qu_rs = query(cursor, sql)
    # print(qu_rs)
    if qu_rs is not None:
        return False
    else:
        return True

# sqlce = "SELECT * FROM [dbo].[kx-知识产权] WHERE [标题] = '2020年全国专利代理师资格考试常见问题解答'"
# selectsql(sqlce)

# sqlcs =  sesql = "SELECT * FROM [dbo].[hb-环保局] WHERE [标题] = '" + "关于发布《一般工业固体废物贮存、处置场污染控制标准》（GB18599- 2001）等3项国家污染物控制标准修改单的公告" + "'"
# selectsql(sqlcs)
#
#
# htmll = '<p style="FONT-SIZE: 16pt;TEXT-ALIGN: right; MARGIN-BOTTOM: 0px; FONT-FAMILY: 仿宋_GB2312; MARGIN-TOP: 0px; TEXT-ALIGN: center; LINE-HEIGHT: 1.5">卫生部令 <br>（第59号）</p> <a href="http://www.mee.gov.cn/xxgk2018/xxgk/xxgk10/../../ywgz/gtfwyhxpgl/gtfw/202005/t20200525_780674.shtml">关于促进砂石行业健康有序发展的指导意见</a><a href="./W020200521583312419148.pdf">sasdad</a><span style="font-family: 仿宋,仿宋_GB2312; font-size: 16pt;"><font face="仿宋_GB2312" style="font-family: 仿宋,仿宋_GB2312; font-size: 16pt;">国家卫生健康委</font></span><span style="font-family: 仿宋,仿宋_GB2312; font-size: 16pt;"><o:p></o:p></span>'
#
# tesss = BeautifulSoup(htmll, "html.parser")
# cc = re.compile(r'TEXT-ALIGN: right', re.I)
# for test in tesss.find_all('p'):
#     if cc.findall(test.get('style')):
#         test.attrs = {"style": "text-align: right"}
#     elif test.get('style') == re.compile("text-align:right"):
#         test.attrs = {"style": "text-align:right"}
#     elif test.get('align') != "client" or test.get('align') != "client":
#         test.attrs = {}
#     elif test.get('style') != "client" or test.get('align') != "client":
#         test.attrs = {}
# print(tesss)
# # #
# # tds = """{text}"""
# tesss = BeautifulSoup(htmll, "html.parser")
#
# test=tesss.find('p')
# nn=test.get('style')
# print(nn)
# cc = re.compile(r'TEXT-ALIGN', re.I).findall(nn)
# print(cc)
# if cc.findall(nn):
#     print(nn)
# for test in tesss.find_all('a'):
#     if test.get('href') is re.compile('.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz)+$'):
#         print(test.get('href'))
# tesss = _remove_attrs(tesss)
#
# cc=tesss.find_all('a')
# for c in cc:
#     print(c)


# for test in tesss.find_all('a', href=re.compile('.html')):
#     test.replace_with(BeautifulSoup(tds.format(text=test.text), 'html.parser'))
#
# for test in tesss.find_all('p'):
#     if test.get('style') == re.compile("text-align: right"):
#         test.attrs = {"style": "text-align: right"}
#     elif test.get('align') != "client" or test.get('align') != "client":
#         test.attrs = None
#     elif test.get('style') != "client" or test.get('align') != "client":
#         test.attrs = None
#
# print(tesss)
# #
# # for test in tesss.find_all('p', style=re.compile("text-align: right")):
# #     test.attrs = {"style": "text-align: right"}
# # for test in tesss.find_all('span'):
# #     test.attrs = None
# # for test in tesss.find_all('font'):
# #     test.attrs = None
# # print(tesss)
# # url = 'http://www.mee.gov.cn/ywgz/fgbz/bz/dfhjbhbzba/'
# # response = requests.get(url)
# #
# response.encoding = "utf-8"
#
# soup = BeautifulSoup(response.text, "html.parser")
#
# print(response.encoding)
# # print(response.text)
# print(soup.find_all('ul', id='div'))
# ul = soup.find('ul', id='div')
# li = ul.find_all('li')
# aurls = []
# for cc in li:
#     aurl = url
#     sss = cc.find('a').get('href')
#     tetil = cc.find('a').text
#     date0 = cc.find('span').text
#     aurl += sss
#     # rep = requests.get(aurl)
#     # aurl = rep.url
#     # aurls.append(aurl)
#     # print(aurls)
#     # # rep = requests.get(aurls[0])
#     #
#     # urll = 'http://www.mee.gov.cn/ywgz/fgbz/bz/dfhjbhbzba/202007/t20200710_788829.shtml'
#     rep = requests.get(aurl)
#     rep.encoding = "utf-8"
#     sub = BeautifulSoup(rep.text, "html.parser")
#
#     # comments = sub.findAll(text=lambda text: isinstance(text, Comment))
#     # [comment.extract() for comment in comments]
#     # # sub = sub.body.contents
#     nn = sub.find('div', class_="TRS_Editor")
#
#     # nn.find('td')
#     # [s.extract() for s in nn('p', align="center")]
#     # [s.extract() for s in nn('td', align="center")]
#     # [s.get('style').extract() for s in nn('td')]
#     # tds = """
#     #   <td><p>{text}</p></td>
#     # """
#     # ps = """
#     #
#     # """
#     # trs = """
#     #   <tr>{text}</tr>
#     # """
#     # # td = nn.find('td')
#     p1 = r"<td([.\n]*).*?>"
#     # print(td)
#
#     # for td in nn.find_all('td'):
#     #     td.replace_with(BeautifulSoup(tds.format(text=td.text), 'html.parser'))
#     # for p in td.find_all('p'):
#     #     p.replace_with(BeautifulSoup(ps.format(text=p), 'html.parser'))
#     # [s.extract() for s in nn('tr')]
#     # print(nn)
#     # print(nn.prettify())
#     # print(nn)
#     # print(li.find('a').get('href'))
#
#     regex = r"(\t|\r|\n|\f|&nbsp)"
#     subst = ""
#     cc = ""
#     # for test in nn.find_all('td'):
#     #     test = re.sub(regex, subst, str(test), 0)
#     nn = BeautifulSoup(re.sub(regex, subst, str(nn), 0), "html.parser")
#     nn = _remove_attrs(nn)
#     #
#     #
#     # nn = _remove_attrs(nn)
#     print(nn)
#     print(tetil)
#     print(date0)
#
# # print(cc)
