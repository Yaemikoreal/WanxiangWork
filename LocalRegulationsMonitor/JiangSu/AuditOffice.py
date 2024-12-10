import difflib
import os
import random
import re
import time

import requests
from bs4 import BeautifulSoup, NavigableString
from datetime import datetime
from elasticsearch import Elasticsearch
from tqdm import tqdm
from urllib3 import disable_warnings
import logging
from query import PublicFunction as pf

# 配置根记录器
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 获取日志记录器
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)
# Elasticsearch 配置
es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


class AuditOffice:
    def __init__(self, **kwargs):
        self.shouludate = "JX" + str(datetime.now().strftime("%Y.%m.%d"))
        self.center_url = 'https://jssjt.jiangsu.gov.cn'
        self.title_url = kwargs.get("start_url")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0",
        }
        self.department_dt = {
            "江苏省市场监督管理局": '8;810;81003;810030380',
            "江苏省审计厅": '8;810;81003;810030295'
        }
        self.category = kwargs.get("category")
        self.department = self.department_dt.get(kwargs.get("lasy_department"))
        self.title_url_lt = kwargs.get("title_url_lt")

    def check_elasticsearch_existence(self, title, index, wenhao=None):
        """
        检查 Elasticsearch 中是否存在给定标题的文章。

        参数:
        title (str): 文章标题。

        返回:
        bool: 如果文章不存在返回 True，否则返回 False。
        """
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "match_phrase": {
                                "标题": {
                                    "query": title,
                                    "slop": 0,
                                    "zero_terms_query": "NONE",
                                    "boost": 1.0
                                }
                            }
                        }
                    ]
                }
            },
            "from": 0,
            "size": 10
        }
        response = es.search(index=index, body=query_body)
        data_nums = int(response['hits']['total'])
        if data_nums == 0:
            # _log.info(f"文章[{title}]不存在于ES")
            return True
        data_lt = response['hits']['hits']
        for it in data_lt:
            read_source = it.get('_source')
            read_wenhao = read_source.get('发文字号')
            read_title = read_source.get('标题')
            if read_wenhao and wenhao:
                if self.is_similar_sequence_matcher(wenhao, read_wenhao):
                    # _log.info(f"文章[{title}]已经存在于es")
                    return False
            else:
                if self.is_similar_sequence_matcher(title, read_title):
                    # _log.info(f"文章[{title}]已经存在于es")
                    return False
        return True

    def title_filter(self, title):
        """
        用于根据文章标题来筛除一些不需要的文章，包含以下关键词的标题的文章都不要
        适用于：其他文件，地区性文件(收录规范性文件、工作文件)
        :param title:包含法规标题
        :return: 如果需要则返回True
        """
        # '政策解读', '答记者问' 争议
        # 排除关键字
        excluded_keywords = {
            '公告', '通报', '通告', '公示', '资质审批名单', '征求意见稿', '备案', '面试名单',
            '培训会', '核准', '公布表', '获批', '予以备案', '备案公告', '报告', '资源包下载',
            '活动情况', '诉求清单', '聘用', '招聘启事', '人员启事', '招聘人员面试', '赛的通知',
            '公告', '公示', '采购意向', '的通告', '视频解读', '邀请函', '图解', '一图读懂',
            '动画解读', '一图看懂', '图文', '视频', '音频', '会议通知', '评估'}
        # 排除后缀
        excluded_suffixes = {
            '公告', '通报', '通告', '公示', '资质审批名单', '征求意见稿', '备案', '面试名单',
            '工作', '培训会', '核准', '公布表', '获批', '予以备案', '备案公告', '报告', '资源包下载', '评估',
            '活动情况',
            '诉求清单'}
        # 针对地方法规文件，不录入国务院等中央文件
        department_not_dt = {
            '国务院'
        }
        # 检查是否以排除后缀结尾
        if any(title.endswith(suffix) for suffix in excluded_suffixes):
            return False
        # 检查是否包含排除关键字
        if any(keyword in title for keyword in excluded_keywords):
            return False
        # 检查部门信息
        if any(keyword in title for keyword in department_not_dt):
            return False
        return True

    def wenhao_get(self, any_soup):
        result_dt = {}
        try:
            msg_table = any_soup.find('table', attrs={'class': 'xxgk_table'})
            tr_all = msg_table.find_all('tr')
            for tr in tr_all:
                count_status = None
                td_all = tr.find_all('td')
                for td in td_all:
                    td_text = td.get_text().replace(" ", '').replace('-', '.').replace(' ', '')
                    if count_status == "文号":
                        result_dt[count_status] = td_text
                        break
                    if count_status == "发文日期":
                        result_dt[count_status] = td_text
                        break
                    if "文号" in td_text:
                        count_status = "文号"
                        continue
                    if "发文日期" in td_text:
                        count_status = "发文日期"
                        continue
        except Exception as e:
            _log.error("该文章没有表格内容!")
        return result_dt

    def remove_nbsp(self, soup):
        """
        对初步清洗的soup进行进步格式清洗
        :param soup: 初步清洗的soup
        :return: 最终结果
        """
        # 遍历所有的文本节点
        for tag in soup.find_all(True):
            if tag.string and isinstance(tag.string, NavigableString):
                # 检查 tag 是否包含文本，并且确保它是 NavigableString 类型
                # 将非换行空格替换为空格
                new_string = tag.string.replace(' ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(' ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace('  ', " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(" ", " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace("  ", " ")
                tag.string.replace_with(new_string)
                new_string = tag.string.replace(" ", " ")
                tag.string.replace_with(new_string)
        a = re.compile(r'\n|&nbsp|&nbsp;|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\t|\r|\f|&ensp;|&emsp;|&emsp|&ensp|\?|？| ')
        soup = BeautifulSoup(a.sub('', str(soup)), "html.parser")

        # remove_text_lt = ['video', 'p']
        # for it_t in remove_text_lt:
        #     # 遍历所有的对应标签
        #     for span in soup.find_all(it_t):
        #         # 如果对应标签的文本为空，则移除它
        #         if not span.get_text().strip():
        #             span.decompose()

        remove_all_lt = ['script']
        for it_a in remove_all_lt:
            # 删除所有的对应标签
            for img in soup.find_all(it_a):
                img.decompose()

        # 如果有抄送，删除抄送
        for it in soup.find_all('p'):
            tag_text = it.get_text()
            if "抄送" in tag_text:
                it.decompose()
        # 将 soup 转换为字符串
        html_str = str(soup)
        # 使用正则表达式移除 HTML 注释
        html_str_without_comments = re.sub(r'<!--(.*?)-->', '', html_str, flags=re.DOTALL)
        # 重新解析成一个新的 soup 对象
        soup = BeautifulSoup(html_str_without_comments, 'html.parser')
        return soup

    def public_down(self, url, save_path):
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

    def annex_get_all(self, result_dt, full_text, any_title, any_url):
        """
        附件获取
        :param result_dt:
        :param full_text:
        :param any_title:
        :return:
        """
        file_path = fr"E:/JXdata/江苏省数据收录/江苏省审计厅/"
        # 检测路径是否存在
        if not os.path.exists(file_path):
            # 如果路径不存在，则创建路径
            os.makedirs(file_path)
            _log.info(f"创建路径: 目录 [{file_path}] 已创建。")
        fujian = []
        replaced_full = full_text
        for test in full_text.find_all('a', href=re.compile(
                '.*?(pdf|docx|doc|xlsx|xls|rar|zip|jpeg|jpg|png|gif|txt|7z|gz|PDF|ppt)+$')):
            src_c = test.get('href').replace('jspclassid', 'jsp?classid')
            # 江苏省市场监督管理局特用
            href_c = self.center_url+ '/' + src_c
            # 从URL参数中提取'filename'的值
            filename = href_c.split('&filename=')[-1]
            if 'http' in filename:
                filename = filename.split('/')[-1]
            # ysrcs = ysrc.split("/")
            # wjm = ysrcs[len(ysrcs) - 1]
            # if '?' in wjm:
            #     wjm = wjm.split('?')
            #     wjm = wjm[0]
            if href_c:
                ysrca = '/datafolder/附件/' + 'lar' + '/' + filename
                replaced_full = str(replaced_full).replace(href_c, ysrca)
                try:
                    self.public_down(href_c, file_path + filename)
                    time.sleep(random.uniform(2, 4))
                    fujian.append({"Title": any_title, "SavePath": ysrca, "Url": any_url})
                except Exception as e:
                    _log.error(f"附件下载出错： {e}")
                    test.attrs = {'href': ysrca}
                    fujian.append({"Title": any_title, "SavePath": ysrca, "Url": any_url})
        if 'img' in str(full_text):
            for img in full_text.find_all('img'):
                src_i = img.get('src')
                if src_i:
                    file_name = src_i.split('/')[-1]
                    file_name = file_name.rstrip('?vpn-1')

                    ysrca = os.path.join('/datafolder/附件/' + 'lar' + '/' + file_name)
                    replaced_full = str(replaced_full).replace(src_i, ysrca)
                    src_i = self.center_url + src_i
                    try:
                        self.public_down(src_i, file_path + file_name)
                        fujian.append({"Title": any_title, "SavePath": ysrca, "Url": src_i})
                        time.sleep(random.uniform(2, 4))
                    except Exception as e:
                        _log.error(f"Error downloading {src_i}: {e}")

                    img.attrs = {'src': ysrca}
        result_dt['附件'] = ""
        result_dt['全文'] = full_text
        return result_dt

    def is_similar_sequence_matcher(self, s1, s2, threshold=0.95):
        matcher = difflib.SequenceMatcher(None, s1, s2)
        similarity = matcher.ratio()
        return similarity >= threshold

    def process_data(self, data_lt):
        count_num = 0
        # 批量检查 Elasticsearch 中是否存在数据
        existing_titles = {item['标题'] for item in data_lt if
                           self.check_elasticsearch_existence(item.get('标题'), 'lar', item.get("文号"))}

        # 筛选出需要处理的数据
        to_insert = [it for it in data_lt if it['标题'] in existing_titles]

        # 批量查询 47 数据库中已存在的数据
        titles_to_check = [f"'{it['标题']}'" for it in to_insert]
        if titles_to_check:
            sql = f"SELECT [法规标题] FROM [自收录数据].dbo.[专项补充收录] WHERE [法规标题] IN ({', '.join(titles_to_check)})"
            results = pf.query_sql_BidDocument(sql)
            existing_titles_in_db = {row[0] for row in results}
        else:
            existing_titles_in_db = set()

        # 准备批量插入的数据
        insert_data = []
        for it in to_insert:
            if it['标题'] in existing_titles_in_db:
                # _log.info(f"47数据库中已经存在 [{it['标题']}] 这条数据!")
                continue

            # 使用参数化查询防止 SQL 注入
            insert_data.append((
                it['唯一标志'], it['标题'], it['全文'], it['发布部门'], it['来源'], it['附件'],
                it['发文日期'], it['文号'], it['收录时间'], it['发文日期'], it['效力级别'], it['类别']
            ))

        # # 批量插入数据
        # if insert_data:
        insert_sql = """
            INSERT INTO [dbo].[专项补充收录] 
            (唯一标志, 法规标题, 全文, 发布部门, 来源, 附件, 发布日期, 发文字号, 收录时间, 实施日期, 效力级别,类别) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        # 尝试逐条插入
        _log.info(f"最终需要写入的数据量为:[{len(insert_data)}]条!")
        for it in insert_data:
            try_num = 3
            while try_num > 0:
                try:
                    single_insert_sql = insert_sql.replace('?', "'{}'").format(*it)
                    pf.save_sql_BidDocument(single_insert_sql)
                    count_num += 1
                    _log.info(f"[{count_num}][{it[1]}] 写入成功!")
                    break
                except Exception as e:
                    _log.error(f"单条插入失败: {e}, 重试")
                    time.sleep(random.uniform(0.5, 1))
                    try_num -= 1
            _log.info("====" * 20)
        return count_num

    def full_cal(self, any_soup, any_title, any_url):
        """
        处理正文，发文字号
        :param any_soup: 文章的soup
        :param any_title: 文章的标题
        :param any_url: 文章的url
        :return:
        """
        # 发文字号
        result_dt = self.wenhao_get(any_soup)
        status = True
        if not self.check_elasticsearch_existence(any_title, 'lar', result_dt.get("文号")):
            _log.info(f"存在这篇文章: [{any_title}]")
            status = False
        else:
            _log.info(f"正在收录文章: [{any_title}]")
            try:
                full_date = any_soup.find('span', attrs={"class": "date"})
                full_date = full_date.get_text().replace("发布日期：", "")
                # 解析原始字符串为 datetime 对象
                date_object = datetime.strptime(full_date, '%Y-%m-%d %H:%M')
                # 格式化日期对象为新的字符串
                full_date = date_object.strftime('%Y.%m.%d')
                result_dt["发布日期"] = full_date
            except Exception as e:
                result_dt["发布日期"] = result_dt.get('发文日期')
            # 全文以及格式处理
            full_text = any_soup.find(['div','td'], attrs={"class": ["main-txt","bt_content"]})
            result_dt = self.annex_get_all(result_dt, full_text, any_title, any_url)
            result_dt['全文'] = pf.soup_cal(result_dt['全文'])
            result_dt['全文'] = self.remove_nbsp(result_dt['全文'])
            result_dt["全文"] = str(result_dt['全文'])
        return result_dt, status

    def get_fulltext(self):
        """
        处理每一篇文章内容
        :return: 处理好的文章列表
        """
        data_lt = []
        for it in self.title_url_lt:
            any_title = it.get("标题")
            # 标题过滤
            if not self.title_filter(any_title):
                _log.info(f"[{any_title}] 该文章无需录入,标题筛查未通过。")
                _log.info("===="*20)
                continue
            # if any_title != '江苏省广告产业园区管理办法解读':
            #     continue
            any_url = it.get("来源")
            _log.info(f"正在收录[{any_title}]")
            time.sleep(random.uniform(0.2, 0.5))
            any_soup = pf.fetch_url(any_url, self.headers)
            # 正文处理,发文日期,发文字号
            result_dt, status = self.full_cal(any_soup, any_title, any_url)
            if not status:
                _log.info("====" * 20)
                continue
            # 唯一标志
            md5_title_value = pf.get_md5(any_title)
            result_dt['唯一标志'] = md5_title_value
            result_dt['来源'] = any_url
            result_dt['标题'] = any_title
            result_dt['发布部门'] = self.department
            result_dt["收录时间"] = self.shouludate
            result_dt["效力级别"] = "XP10"
            # 计算类别
            category = pf.catagroy_select(result_dt['全文'], result_dt['标题'])
            if category:
                result_dt["类别"] = category
            else:
                result_dt["类别"] = self.category

            data_lt.append(result_dt)
            _log.info(f"[{result_dt['标题']}] 收录完毕!")
            _log.info("====" * 20)
        return data_lt

    def calculate(self):
        data_lt = self.get_fulltext()
        self.process_data(data_lt)


def main(data_dt):
    obj = AuditOffice(**data_dt)
    obj.calculate()


if __name__ == '__main__':
    data_dt = {
        "start_url": 'https://jw.cq.gov.cn/zwgk/zfxxgkml/zcwj/gfxwj/',  # 访问路径
        "lasy_department": '江苏省市场监督管理局',  # 在函数返回为空的时候指定发布部门
        "category": "096;09618"
    }
    main(data_dt)
