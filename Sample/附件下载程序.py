# coding=utf-8
import requests
import re
import os, os.path, shutil

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
}

"""
    备注：附件下载程序现在新增了 附件下载下载错误时返回一个状态码，由调用的人去具体实现想要的结果;成功为True，失败为False

"""


# 这种方法是用于下载的具体的方法，没有传入header，不知道为什么，再有的时候传入header之后下载下来的文件存在问题 ：http://xxgk.hainan.gov.cn/qhxxgk/wtj/201901/P020190114624769074502.xls
def public_down(url, save_path):
    # print(f"完整的保存地址 {save_path}")
    requests.packages.urllib3.disable_warnings()
    req = requests.get(url, headers=headers, verify=False)
    try:
        if req.status_code == 200:
            with open('C:/Users/admin/PycharmProjects/pythonProject/fujian'+save_path, "wb") as c:
                c.write(req.content)
            # time.sleep(10)
            print("下载成功")
            return "ok"
        elif req.status_code == 521:
            print(55)
            # cookies = req.cookies
            # cookies = '; '.join(['='.join(item) for item in cookies.items()])
            # txt_521 = req.text
            # txt_521 = ''.join(re.findall('<script>(.*?)</script>', txt_521))
            # print(txt_521)
            # return (txt_521, cookies)
        elif req.status_code == 404:
            print("下载失败，网页打不开！！！")
            print(url)
            return "fail,下载失败，网页打不开！！！ "
    except Exception as c:
        print(c)


def public_downs(url, save_path):
    try:
        public_down(url, save_path)
    except Exception as c:
        public_downs(url, save_path)


# 这种方法是用于下载的具体的方法，没有传入header，不知道为什么，再有的时候传入header之后下载下来的文件存在问题 ：http://xxgk.hainan.gov.cn/qhxxgk/wtj/201901/P020190114624769074502.xls
def download_data(url, save_path, adj_name):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
    }
    mkdir(save_path)
    save_path = save_path + adj_name
    try:
        req = requests.get(url, headers=headers)
        if req.status_code == 200:

            with open(save_path, "wb") as c:
                c.write(req.content)


        elif req.status_code == 521:
            print(55)
            # cookies = req.cookies
            # cookies = '; '.join(['='.join(item) for item in cookies.items()])
            # txt_521 = req.text
            # txt_521 = ''.join(re.findall('<script>(.*?)</script>', txt_521))
            # print(txt_521)
            # return (txt_521, cookies)
    except Exception as c:
        return False
        # logger.error(f"附件下载错误：附件未能下载请手动查看,数据地址url: {content_src}, 附件下载地址： {url} 数据标题： {title}")
        # print(e)
    return True


# 创建目录
def mkdir(path):
    # 去除首位空格
    path = path.strip()

    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print(path + "创建成功")
    else:
        print(path + "目录已存在")

# public_down('http://ybj.hubei.gov.cn/zfxxgk/zc/gfwj/202311/P020231114574661523744.docx', r'C:/Users/小可爱/Desktop/附件/datafolder/新收录/20231114/P020231114574661523744.docx')

# ss = download_data("https://lawdoo.com/datafolder/%E5%9F%8E%E4%B9%A1%E5%BB%BA%E8%AE%BE/%E5%9F%8E%E4%B9%A1%E5%BB%BA%E8%AE%BE/%E5%8D%97%E5%AE%81%E5%B8%82%E5%9F%8E%E5%B8%82%E7%AE%A1%E7%90%86%E7%BB%BC%E5%90%88%E8%A1%8C%E6%94%BF%E6%89%A7%E6%B3%95%E5%B1%80%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A/P020200522348797352876.zip", "D:\\", "P020200522348797352876.zip")
# print(ss)
