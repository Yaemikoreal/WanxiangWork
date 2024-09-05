from bs4 import BeautifulSoup
from datetime import datetime
from botpy import logging
from query import PublicFunction

_log = logging.get_logger()
"""
本方法用于获取重庆市司法局行政规范性文件

url:https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/xzgfxwj/sfzggwxzgfxwj/
"""


class DevelopmentAndReformCommission:
    def __init__(self):
        self.shouludate = "JX" + str(datetime.now().strftime("%Y.%m.%d"))
        self.pf = PublicFunction
        # 初始url
        # self.start_url = 'https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/xzgfxwj/sfzggwxzgfxwj/'
        self.start_url = 'https://fzggw.cq.gov.cn/zwgk/zfxxgkml/zcwj/fzhsxwj/'
        # 请求头
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        # 保留列表
        self.into_lt = ["text-align:right", "text-align:center", "text-align: right","text-align: center"]
        # 发布部门
        self.department_of_publication = {
            "重庆市司法局": "8;831;83103;831030007",
            "重庆市发展和改革委员会": "8;831;83103;831030003",
        }
        # 类别
        self.category = {"机关工作综合规定": "003;00301"}
        # 效力级别
        self.level_of_effectiveness = {"地方规范性文件": "XP08", "地方工作文件": "XP10"}

    def remove_outer_brackets(self, text_remove, end_phrase):
        """
        删除字符串开头和结尾的括号，并保留 发文字号,并删除发文日期
        :param text_remove:
        :param end_phrase:
        :return: 发文字号
        """
        # 移除开头的括号
        if text_remove.startswith('('):
            text_remove = text_remove[1:]
        # 移除结尾的括号
        if text_remove.endswith(')'):
            text_remove = text_remove[:-1]
        # 找到 "发文字号：" 的结束位置
        start_phrase_end = text_remove.find("：", text_remove.find("发文字号"))
        start_index = start_phrase_end + 1
        # 找到 "成文日期" 的开始位置
        end_phrase_start = text_remove.find(end_phrase)
        if end_phrase_start == -1:
            return text_remove  # 如果没有找到结束短语，则返回原字符串
        # 返回 "发文字号：" 和 "成文日期" 之间的文本
        result = text_remove[start_index:end_phrase_start]
        return result

    def title_data_get(self, url):
        """
        用于获取到总页面内容，获取到该页的 标题，发文字号，成文日期
        :return:result_lt：列表套字典，字典装有信息
        """
        result_lt = []
        # 获取到总网页内容
        soup_title_all = self.pf.fetch_url(url=url, headers=self.headers)
        soup_title_all = soup_title_all.find('table', class_='zcwjk-list')
        soup_title_all = soup_title_all.find_all('tr', class_=['zcwjk-list-c clearfix', 'zcwjk-list-c clearfix cur'])
        for tag in soup_title_all:
            title_get = tag.find('p', class_='tit')
            # 标题
            title = title_get.get_text()
            title_url_get = tag.find('a', target="_blank")
            # url 未拼接
            title_url = title_url_get.get('href')
            issued_num_get = tag.find('p', class_='info')
            # 发文字号
            issued_num = issued_num_get.get_text()
            issued_num = self.remove_outer_brackets(issued_num, "成文日期 ")
            issued_date = issued_num_get.find('span', class_='time').get_text()
            # 发布日期
            issued_date = issued_date.lstrip("成文日期 ：")
            issued_date = issued_date.replace("年", ".").replace("月", ".").replace("日", "")

            data_dt = {
                "法规标题": title,
                "法规url": title_url,
                "发文字号": issued_num,
                "发布日期": issued_date
            }
            result_lt.append(data_dt)
        return result_lt

    def zhengwen_get(self, soup):
        # 正文
        class_lt = ['trs_editor_view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word',
                    'view TRS_UEDITOR trs_paper_default trs_word trs_web',
                    'view TRS_UEDITOR trs_paper_default trs_default trs_word trs_web',
                    'trs_editor_view TRS_UEDITOR trs_paper_default trs_external'
                    ]
        zhengwen = soup.find('div', class_='zcwjk-xlcon')
        for it in class_lt:
            zhengwen_stat = zhengwen.find('div', class_=it)
            if zhengwen_stat is not None:
                break
        # 对style标签值进行处理
        if zhengwen:
            soup_ture = self.pf.soup_cal(zhengwen)
            soup_ture = self.pf.remove_nbsp(soup_ture)
        else:
            soup_ture = None
        soup_ture = str(soup_ture)
        return soup_ture

    def calculate_category(self, it):
        # 计算类别编号
        full_text = it.get('全文')
        title = it.get('法规标题')
        # 重新解析成一个新的 soup 对象
        full_text_soup = BeautifulSoup(full_text, 'html.parser')
        # 使用 get_text() 方法获取所有的文本内容
        full_text_only = full_text_soup.get_text()
        catagroy = self.pf.catagroy_select(description=full_text_only, titl=title)
        bumen = self.pf.department(Description=full_text_only, title=title, area_num='831')  # 831:重庆地区
        return catagroy, bumen

    def filter_all(self, new_result_lt):
        for it in new_result_lt:
            _log.info(f"需要写入的文章:{it.get('法规标题')}")
            new_get_url = self.start_url.rstrip('index.html') + it.get('法规url').lstrip('./')
            # soup
            soup = self.pf.fetch_url(new_get_url, headers=self.headers)
            # 正文
            it['全文'] = self.zhengwen_get(soup)
            # 唯一标志
            md5_str = it.get('法规标题') + it.get('发布日期')
            it["唯一标志"] = self.pf.get_md5(md5_str)
            # 来源
            it["来源"] = new_get_url
            # 发布部门
            catagroy, bumen = self.calculate_category(it)
            it["发布部门"] = bumen
            # 类别
            it["类别"] = catagroy
            # 效力级别
            it["效力级别"] = self.level_of_effectiveness['地方规范性文件']
            # 时效性
            it["时效性"] = "01"
            it["实施日期"] = it.get('发布日期')
            del it['法规url']
            sql = rf"INSERT INTO [自收录数据].dbo.[专项补充收录] ([唯一标志],[法规标题],[全文],[发布部门],[类别],[发布日期],[效力级别],[实施日期],[发文字号],[时效性],[来源],[收录时间]) VALUES ('{it['唯一标志']}','{it.get('法规标题')}','{it['全文']}','{it['发布部门']}','{it['类别']}','{it.get('发布日期')}','{it['效力级别']}','{it['实施日期']}','{it['发文字号']}','{it['时效性']}','{it['来源']}','{self.shouludate}')"
            self.pf.save_sql_BidDocument(sql)
            _log.info(f"文章:{it.get('法规标题')}写入完毕！！！")

    def calculate(self):
        # 有几页就遍历几次
        for i in range(1):
            if i == 0:
                new_url = self.start_url
            else:
                new_url = self.start_url + f"index_{i}.html"
            # 获取该页内容信息
            result_lt = self.title_data_get(url=new_url)
            _log.info(f"第{i + 1}页    获取到{len(result_lt)} 篇内容！！！")
            # 过滤已有的文章
            new_result_lt = self.pf.filter(result_lt)
            if not new_result_lt:
                _log.info(f"第{i + 1}页    无内容需要写入！！！")
                continue
            _log.info(f"第{i + 1}页    需要写入的文章有 {len(new_result_lt)} 篇！！！")
            # 统筹整理,写入数据
            self.filter_all(new_result_lt)
            _log.info(f"第{i + 1}页    写入完毕！！！")


def main():
    obj = DevelopmentAndReformCommission()
    obj.calculate()


if __name__ == '__main__':
    main()
