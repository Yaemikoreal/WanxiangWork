import time

from EducationalDocuments import EducationalDocuments
from query import PublicFunction as pf
import re

"""
重庆市科学技术局行政规范性文件
https://kjj.cq.gov.cn/zwgk_176/zwxxgkml/zcwj/xzgfxwj/
获取重庆市教育委员会行政规范性文件
https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/gfxwj/
获取重庆市经济和信息化委员会行政规范性文件
https://jjxxw.cq.gov.cn/zwgk_213/zcwj/xzgfxwj/
获取重庆市民族宗教事务委员会行政规范性文件
https://mzzjw.cq.gov.cn/zfxxgkml/zcwj/gfxwj/
获取重庆市公安局行政规范性文件
https://gaj.cq.gov.cn/zwgk/zcwj/xfgfxwj/
获取重庆市民政局行政规范性文件
https://mzj.cq.gov.cn/zwgk_218/zfxxgkml/zcwj_166256/xzgfxwj1/
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
重庆市体育局行政规范性文件
https://tyj.cq.gov.cn/zwgk_253/zcwj/xzgfxwj/
重庆市统计局行政规范性文件
https://tjj.cq.gov.cn/zwgk_233/zcwj/xzgfxwj/
重庆市医疗保障局行政规范性文件
https://ylbzj.cq.gov.cn/zwgk_535/zfxxgkml/zcwj_291934/gfxwj/
重庆市大数据应用发展管理局行政规范性文件
https://dsjj.cq.gov.cn/zwgk_533/zcwj/zcxzgfxwj/
重庆市人民政府口岸和物流办公室行政规范性文件
https://zfkawlb.cq.gov.cn/zwgk/zcwj/xzgfxwj_345066/
重庆市国防动员办公室行政规范性文件
https://rmfkb.cq.gov.cn/zwgk_246/zfxxgkml/fztd/gfxwj/
重庆市公共资源交易监督管理局行政规范性文件
https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/xzgfxwj/sggzyjyjgjxzgfxwj/
重庆市林业局行政规范性文件
https://lyj.cq.gov.cn/zwgk_237/zfxxgjml/zcwj/xzgfxwj/
重庆市药品监督管理局行政规范性文件
https://yaojianju.cq.gov.cn/zwgk_n2104/zfxxgkml/zcwjn2104/gfxwj/
重庆市知识产权局行政规范性文件
https://zscqj.cq.gov.cn/zwgk_232/zcwj/gfxwj/
重庆两江新区管理委员会行政规范性文件
https://ljxq.cq.gov.cn/zwgk_199/zfxxgkml/xqgw/xzgfxwj/
重庆高新技术产业开发区管理委员会行政规范性文件
https://gxq.cq.gov.cn/zwgk_202/zfxxgkml/zcwj/xzgfxwj/
重庆市万盛经济技术开发区管理委员会行政规范性文件
https://ws.cq.gov.cn/cqws_zwxxgkml/zcwjjjdkcs/zcwj_zfxxgkml/xzgfxwj/

"""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
}
departments = [
    {"部门名称": "巫山县科技技术局", "URL": "http://www.cqws.gov.cn/xzfbm_73744/fzhggwyh_74216/zwgk_72016/fdzdgknr/lzyj2/zcwj_kjj2023/xzgfxwj_kjj/"},
    {"部门名称": "巫山县人民政府", "URL": "http://www.cqws.gov.cn/zwgk_258/zfxxgkml_154818/zcwj/gfxwjhz_2310/w/"},
    {"部门名称": "巫山县规划和自然资源局", "URL": "http://www.cqws.gov.cn/xzfbm_73744/sfj_1/zwgk_72016/fdzdgknr/lzyj2/zcwj_gzj2023/xzgfxwj_gzj/"},
    {"部门名称": "巫山县农业农村委员会", "URL": "http://www.cqws.gov.cn/xzfbm_73744/fzhggwyh_74230/zwgk_72016/fdzdgknr/lzyj2/zcwj_nyw2023/xzgfxwj_nyw/"},
    {"部门名称": "巫山县文化和旅游发展委员会", "URL": "http://www.cqws.gov.cn/xzfbm_73744/fzhggwyh_74090/zwgk_72016/fdzdgknr/lzyj2/zcwj_wlw2023/xzgfxwj_wlw/"},
    {"部门名称": "巫山县应急管理局", "URL": "http://www.cqws.gov.cn/xzfbm_73744/fzhggwyh_74108/zwgk_72016/fdzdgknr/lzyj2/zcwj_yjj2023/xzgfxwj_yjj/"},
    {"部门名称": "巫山县医疗保障局", "URL": "http://www.cqws.gov.cn/xzfbm_73744/fzhggwyh_74162/zwgk_72016/fdzdgknr/lzyj2/zcwj_ybj2023/xzgfxwj_ybj/"},
    {"部门名称": "巫山县抱龙镇人民政府", "URL": "http://www.cqws.gov.cn/xzfjz/blz_73108/zwgk_73112/fdzdgknr_73114/zcwj/xzgfx_blz/"},
    {"部门名称": "巫山县两坪乡人民政府", "URL": "http://www.cqws.gov.cn/xzfjz/blz_77785/zwgk_73112/fdzdgknr_73114/zcwj113/xzgfx_lpx/"},
    {"部门名称": "巫山县建平乡人民政府", "URL": "http://www.cqws.gov.cn/xzfjz/blz_77761/zwgk_73112/fdzdgknr_73114/zcwj/xzgfx_jpx/"},
    {"部门名称": "巫山县大溪乡人民政府", "URL": "http://www.cqws.gov.cn/xzfjz/blz_77290/zwgk_73112/fdzdgknr_73114/zcwj/xzgfx_dxx/"},
    {"部门名称": "巫山县红椿土家族乡人民政府", "URL": "http://www.cqws.gov.cn/xzfjz/blz_77688/zwgk_73112/fdzdgknr_73114/zcwj/xzgfx_hctjz/"},
    {"部门名称": "重庆市科学技术局", "URL": "https://kjj.cq.gov.cn/zwgk_176/zwxxgkml/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市教育委员会", "URL": "https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/gfxwj/"},
    {"部门名称": "重庆市经济和信息化委员会", "URL": "https://jjxxw.cq.gov.cn/zwgk_213/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市民族宗教事务委员会", "URL": "https://mzzjw.cq.gov.cn/zfxxgkml/zcwj/gfxwj/"},
    {"部门名称": "重庆市公安局", "URL": "https://gaj.cq.gov.cn/zwgk/zcwj/xfgfxwj/"},
    {"部门名称": "重庆市民政局", "URL": "https://mzj.cq.gov.cn/zwgk_218/zfxxgkml/zcwj_166256/xzgfxwj1/"},
    {"部门名称": "重庆市司法局", "URL": "https://sfj.cq.gov.cn/zwgk_243/zfxxgkml1/zcwj/sfjgfxwj/xzgfxwj/"},
    {"部门名称": "重庆市财政局", "URL": "https://czj.cq.gov.cn/zwgk_268/zfxxgkml/zcwj/gfxwj/"},
    {"部门名称": "重庆市人力资源和社会保障局", "URL": "https://rlsbj.cq.gov.cn/zwgk_182/zfxxgkml/zcwj_145360/jfxzgfxwj/"},
    {"部门名称": "重庆市规划和自然资源局", "URL": "https://ghzrzyj.cq.gov.cn/zwgk_186/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市生态环境局", "URL": "https://sthjj.cq.gov.cn/zwgk_249/zfxxgkml/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市体育局", "URL": "https://tyj.cq.gov.cn/zwgk_253/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市统计局", "URL": "https://tjj.cq.gov.cn/zwgk_233/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市医疗保障局", "URL": "https://ylbzj.cq.gov.cn/zwgk_535/zfxxgkml/zcwj_291934/gfxwj/"},
    {"部门名称": "重庆市大数据应用发展管理局", "URL": "https://dsjj.cq.gov.cn/zwgk_533/zcwj/zcxzgfxwj/"},
    {"部门名称": "重庆市人民政府口岸和物流办公室", "URL": "https://zfkawlb.cq.gov.cn/zwgk/zcwj/xzgfxwj_345066/"},
    {"部门名称": "重庆市国防动员办公室", "URL": "https://rmfkb.cq.gov.cn/zwgk_246/zfxxgkml/fztd/gfxwj/"},
    {"部门名称": "重庆市公共资源交易监督管理局", "URL": "https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/xzgfxwj/sggzyjyjgjxzgfxwj/"},
    {"部门名称": "重庆市林业局", "URL": "https://lyj.cq.gov.cn/zwgk_237/zfxxgjml/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市药品监督管理局", "URL": "https://yaojianju.cq.gov.cn/zwgk_n2104/zfxxgkml/zcwjn2104/gfxwj/"},
    {"部门名称": "重庆市知识产权局", "URL": "https://zscqj.cq.gov.cn/zwgk_232/zcwj/gfxwj/"},
    {"部门名称": "重庆两江新区管理委员会", "URL": "https://ljxq.cq.gov.cn/zwgk_199/zfxxgkml/xqgw/xzgfxwj/"},
    {"部门名称": "重庆高新技术产业开发区管理委员会", "URL": "https://gxq.cq.gov.cn/zwgk_202/zfxxgkml/zcwj/xzgfxwj/"},
    {"部门名称": "重庆市万盛经济技术开发区管理委员会", "URL": "https://ws.cq.gov.cn/cqws_zwxxgkml/zcwjjjdkcs/zcwj_zfxxgkml/xzgfxwj/"}
]


def filter_soup(script_soup):
    for tag in script_soup:
        tag_text = tag.string
        if tag_text:
            if "createPage" in tag_text:
                # 提取页数
                match = re.search(r'createPage\((\d+)', tag_text)
                if match:
                    page_count = int(match.group(1))
                    print(f"总页数: {page_count}")
                    return page_count
                else:
                    print("未找到页数")
    return None


def monday_inspection():
    for it in departments:
        lasy_department = it.get("部门名称")
        start_url = it.get("URL")
        # soup_title = pf.fetch_url(url=start_url, headers=headers)
        # script_soup = soup_title.find_all('script')
        # read_pages_num = filter_soup(script_soup)
        # if not read_pages_num:
        #     print(f"[{lasy_department}] 未能找到对应页码!")
        #     read_pages_num = 1
        # if read_pages_num > 5:
        #     read_pages_num = 5
        data_dt = {
            "start_url": start_url,  # 访问路径
            "write_table_name": '行政规范性文件',  # 写入表名
            'read_pages_start': 0,  # 读取页码起始数(调试用)
            "read_pages_num": 3,  # 读取页码总数
            "save_path_real": '行政规范性文件',  # 附件存放路径,
            "lasy_department": lasy_department,  # 在函数返回为空的时候指定发布部门
            "level_of_effectiveness": '地方规范性文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
        }
        # print(f"[{lasy_department}] 正在收录: [{start_url}]")
        obj = EducationalDocuments(**data_dt)
        obj.calculate()


def test_main():
    data_dt = {
        "start_url": 'https://ws.cq.gov.cn/cqws_zwxxgkml/zcwjjjdkcs/zcwj_zfxxgkml/xzgfxwj/',  # 访问路径
        "write_table_name": '行政规范性文件',  # 写入表名
        'read_pages_start': 0,  # 读取页码起始数(调试用)
        "read_pages_num": 5,  # 读取页码总数
        "save_path_real": '行政规范性文件',  # 附件存放路径,
        "lasy_department": '重庆市万盛经济技术开发区管理委员会',  # 在函数返回为空的时候指定发布部门
        "level_of_effectiveness": '地方规范性文件',  # 指定效力级别,如果不填，则默认为地方规范性文件
    }
    obj = EducationalDocuments(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    monday_inspection()
