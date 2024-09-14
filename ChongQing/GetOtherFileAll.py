from GetOtherFile import GetOtherFile

"""
重庆市教育委员会其他文件
https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/qtwj/
重庆市科学技术局其他文件
https://kjj.cq.gov.cn/zwgk_176/zwxxgkml/zcwj/qtwj/
重庆市经济和信息化委员会其他文件
https://jjxxw.cq.gov.cn/zwgk_213/zcwj/qtwj/
重庆市民族宗教事务委员会其他文件
https://mzzjw.cq.gov.cn/zfxxgkml/zcwj/qtwj/
重庆市公安局其他文件
https://gaj.cq.gov.cn/zwgk/zcwj/qtgw/
重庆市民政局其他文件
https://mzj.cq.gov.cn/zwgk_218/zfxxgkml/zcwj_166256/qtwj_166259/
重庆市司法局其他文件
https://sfj.cq.gov.cn/zwgk_243/zfxxgkml/sflzyj/sfjqtwj/
重庆市财政局其他文件
https://czj.cq.gov.cn/zwgk_268/zfxxgkml/zcwj/qtwj/
重庆市人力社保局其他文件
https://rlsbj.cq.gov.cn/zwgk_182/zfxxgkml/zcwj_145360/qtwj/
重庆市规划和自然资源局其他文件
https://ghzrzyj.cq.gov.cn/zwgk_186/zcwj/qtwj/
重庆市生态环境局
https://sthjj.cq.gov.cn/zwgk_249/zfxxgkml/zcwj/qtwj/
重庆市体育局
https://tyj.cq.gov.cn/zwgk_253/zcwj/qtwj/
重庆市统计局
https://tjj.cq.gov.cn/zwgk_233/zcwj/qtwj/
重庆市医疗保障局(无)
https://ylbzj.cq.gov.cn/zwgk_535/zfxxgkml/zcwj_291934/qtwj222/
重庆市大数据应用发展管理局
https://dsjj.cq.gov.cn/zwgk_533/zcwj/zcqtwj/
重庆市人民政府口岸和物流办公室
https://zfkawlb.cq.gov.cn/zwgk/zcwj/qtwj_345067/
重庆市国防动员办公室
https://rmfkb.cq.gov.cn/zwgk_246/fdzdgknr/lzyj/qtwj_40921/
重庆市公共资源交易监督管理局
(隶属于发改委）已收录
重庆市林业局
https://lyj.cq.gov.cn/zwgk_237/zfxxgjml/zcwj/qtwj/
重庆市药品监督管理局
https://yaojianju.cq.gov.cn/zwgk_n2104/zfxxgkml/zcwjn2104/qtwjn2104/
重庆市知识产权局
https://zscqj.cq.gov.cn/zwgk_232/zcwj/qtwj/
重庆两江新区管理委员会
https://ljxq.cq.gov.cn/zwgk_199/zfxxgkml/xqgw/qtwj/
重庆高新技术产业开发区管理委员会
https://gxq.cq.gov.cn/zwgk_202/zfxxgkml/zcwj/qtgw/
重庆市万盛经济技术开发区管理委员会
https://ws.cq.gov.cn/cqws_zwxxgkml/zcwjjjdkcs/zcwj_zfxxgkml/
"""


def main_test():
    data_dt = {
        "start_url": 'https://ws.cq.gov.cn/cqws_zwxxgkml/zcwjjjdkcs/zcwj_zfxxgkml/',  # 访问路径
        "write_table_name": '重庆市其他文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 24,  # 读取页码总数
        "save_path_real": '重庆市其他文件',  # 附件存放路径,
        "lasy_department": '重庆市万盛经济技术开发区管理委员会',  # 在函数返回为空的时候指定发布部门
        "level_of_effectiveness": '地方工作文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
    }
    obj = GetOtherFile(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    main_test()
