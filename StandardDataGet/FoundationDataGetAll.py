import time

from FoundationDataGet import FoundationData as fd
from FoundationDataReal import FoundationData as fdr

"""
该方法作用是直接对tools/标准号1.xlsx文件中的标准进行基础信息获取，并整合信息内容写入47数据库
写入表:[自收录数据][dbo].[标准库_国家行业标准]
数据来源:中国标网
"""


def main():
    fd_obj = fd()
    fd_obj.calculate()
    time.sleep(5)
    fdr_obj = fdr()
    fdr_obj.calculate()


if __name__ == '__main__':
    main()
