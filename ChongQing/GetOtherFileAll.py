from GetOtherFile import GetOtherFile
"""
重庆市教育委员会其他文件
https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/
重庆市科学技术局其他文件
https://kjj.cq.gov.cn/zwgk_176/zwxxgkml/zcwj/qtwj/
重庆市经济和信息化委员会其他文件
https://jjxxw.cq.gov.cn/zwgk_213/zcwj/qtwj/
"""

def main_test():
    data_dt = {
        "start_url": 'https://jjxxw.cq.gov.cn/zwgk_213/zcwj/qtwj/',  # 访问路径
        "write_table_name": '重庆市其他文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 76,  # 读取页码总数
        "save_path_real": '重庆市其他文件',  # 附件存放路径,
        "lasy_department": '重庆市经济和信息化委员会',  # 在函数返回为空的时候指定发布部门
        "level_of_effectiveness": '地方工作文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
    }
    obj = GetOtherFile(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main_test()
