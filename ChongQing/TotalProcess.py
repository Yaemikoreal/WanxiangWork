from ChongqingScience import monday_inspection as law_monday_inspection
from GetOtherFileAll import monday_inspection as file_monday_inspection
from NewLawsGet.ProcessingMethod.decorators import timer

"""
重庆市政府部门行政规范性文件和其他文件，以及巫山县文件
本脚本用于每周一执行更新检查，每周一跑一次
数据输出于 自收录数据 专项补充收录 表中
附件输出于Jxdata/重庆市其他文件 或者 行政规范性文件
"""


@timer
def main():
    law_monday_inspection()
    file_monday_inspection()


if __name__ == '__main__':
    main()
