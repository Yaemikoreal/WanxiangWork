from EducationalDocuments import EducationalDocuments

"""
重庆市科学技术局行政规范性文件
https://kjj.cq.gov.cn/zwgk_176/zwxxgkml/zcwj/xzgfxwj/
获取重庆市教育委员会行政规范性文件
url:https://kjj.cq.gov.cn/zwgk_176/zwxxgkml/zcwj/xzgfxwj/
获取重庆市经济和信息化委员会行政规范性文件
url:https://jjxxw.cq.gov.cn/zwgk_213/zcwj/xzgfxwj/
获取重庆市民族宗教事务委员会行政规范性文件
url:https://mzzjw.cq.gov.cn/zfxxgkml/zcwj/gfxwj/
获取重庆市公安局行政规范性文件
url:https://gaj.cq.gov.cn/zwgk/zcwj/xfgfxwj/
获取重庆市民政局行政规范性文件
url:https://mzj.cq.gov.cn/zwgk_218/zfxxgkml/zcwj_166256/xzgfxwj1/
获取重庆市司法局行政规范性文件
https://sfj.cq.gov.cn/zwgk_243/zfxxgkml1/zcwj/sfjgfxwj/xzgfxwj/
重庆市财政局行政规范性文件
https://czj.cq.gov.cn/zwgk_268/zfxxgkml/zcwj/gfxwj/
重庆市人力资源和社会保障局行政规范性文件
https://rlsbj.cq.gov.cn/zwgk_182/zfxxgkml/zcwj_145360/jfxzgfxwj/
重庆市规划和自然资源局行政规范性文件
https://ghzrzyj.cq.gov.cn/zwgk_186/zcwj/xzgfxwj/
重庆市生态环境局行政规范性文件
https://sthjj.cq.gov.cn/zwgk_249/zfxxgkml/zcwj/xzgfxwj/
"""


def main():
    data_dt = {
        "start_url": 'https://sthjj.cq.gov.cn/zwgk_249/zfxxgkml/zcwj/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        "read_pages_num": 7,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径
        "lasy_department": '重庆市生态环境局'  # 在函数返回为空的时候指定发布部门
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main()
