# coding=utf-8
from botpy import logging
import requests
import re
import os,  os.path, shutil
from tqdm import tqdm
from urllib3 import disable_warnings
_log = logging.get_logger()
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
}

"""
    备注：附件下载程序现在新增了 附件下载下载错误时返回一个状态码，由调用的人去具体实现想要的结果;成功为True，失败为False

"""


def public_down(url, save_path):
    _log.info(f'正在下载附件 {url}')

    # 确保保存路径的父目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36',
    }
    # 禁用urllib3的警告
    disable_warnings()

    try:
        with requests.get(url, headers=headers, stream=True, verify=False) as req:
            if req.status_code == 200:
                total_size = int(req.headers.get('content-length', 0))  # 获取文件总大小
                block_size = 1024 * 1024  # 每次读取的块大小为1MB
                t = tqdm(total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(save_path))  # 初始化进度条

                with open(save_path, "wb") as f:
                    for data in req.iter_content(block_size):
                        t.update(len(data))  # 更新进度条
                        f.write(data)
                t.close()

                if total_size != 0 and t.n != total_size:
                    _log.error("ERROR, something went wrong")
                _log.info(f"该附件下载完毕: [{save_path}]")

            elif req.status_code == 521:
                _log.error("状态码521 - 需要进一步处理")
                # 处理状态码521的逻辑可以在此添加

            elif req.status_code == 404:
                _log.error("下载失败，网页打不开！！！")
                _log.info(url)

            else:
                _log.error(f"未知的状态码: {req.status_code}")

    except Exception as e:
        _log.error(f"请求失败: {e}")

# 这种方法是用于下载的具体的方法，没有传入header，不知道为什么，再有的时候传入header之后下载下来的文件存在问题 ：http://xxgk.hainan.gov.cn/qhxxgk/wtj/201901/P020190114624769074502.xls
# def public_down(url, save_path):
#     # print(f"完整的保存地址 {save_path}")
#     requests.packages.urllib3.disable_warnings()
#     req = requests.get(url, headers=headers, verify=False)
#     try:
#         if req.status_code == 200:
#             with open(save_path, "wb") as f:
#                 f.write(req.content)
#             # time.sleep(10)
#             # print("下载成功")
#             return "ok"
#         elif req.status_code == 521:
#             print(55)
#             # cookies = req.cookies
#             # cookies = '; '.join(['='.join(item) for item in cookies.items()])
#             # txt_521 = req.text
#             # txt_521 = ''.join(re.findall('<script>(.*?)</script>', txt_521))
#             # print(txt_521)
#             # return (txt_521, cookies)
#         elif req.status_code == 404:
#             print("下载失败，网页打不开！！！")
#             print(url)
#             return "fail,下载失败，网页打不开！！！ "
#     except Exception as e:
#         print(e)


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

            with open(save_path, "wb") as f:
                f.write(req.content)


        elif req.status_code == 521:
            print(55)
            # cookies = req.cookies
            # cookies = '; '.join(['='.join(item) for item in cookies.items()])
            # txt_521 = req.text
            # txt_521 = ''.join(re.findall('<script>(.*?)</script>', txt_521))
            # print(txt_521)
            # return (txt_521, cookies)
    except Exception as e:
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

# public_down('https://resources.pkulaw.cn/staticfiles/20190702/21/18/5/eabc792ffde58b06bb718b012b02825c.docx', r'F:\附件补充下载\eabc792ffde58b06bb718b012b02825c.docx')

# ss = download_data("https://lawdoo.com/datafolder/%E5%9F%8E%E4%B9%A1%E5%BB%BA%E8%AE%BE/%E5%9F%8E%E4%B9%A1%E5%BB%BA%E8%AE%BE/%E5%8D%97%E5%AE%81%E5%B8%82%E5%9F%8E%E5%B8%82%E7%AE%A1%E7%90%86%E7%BB%BC%E5%90%88%E8%A1%8C%E6%94%BF%E6%89%A7%E6%B3%95%E5%B1%80%E8%A1%8C%E6%94%BF%E5%A4%84%E7%BD%9A/P020200522348797352876.zip", "D:\\", "P020200522348797352876.zip")
# print(ss)