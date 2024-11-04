import os
import pandas as pd
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
from query.PublicFunction import load_config
from ProcessingMethod.LoggerSet import logger

"""
该方法用于手动处理目录数据
依赖于 附件/html.text获取的search信息
"""
# 配置日志


# 加载配置
env = os.getenv('FLASK_ENV', 'test')
app_config = load_config(env)
ES_HOSTS = app_config.get('es_hosts')
ES_HTTP_AUTH = tuple(app_config.get('es_http_auth').split(':'))

# 创建Elasticsearch客户端
es_client = Elasticsearch([ES_HOSTS], http_auth=ES_HTTP_AUTH)


def check_article_exists(title, index_name='lar'):
    """
    检查 Elasticsearch 中是否存在给定标题的文章。

    参数:
    title (str): 文章标题。
    index_name (str): Elasticsearch 索引名称，默认为 'lar'。

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
    response = es_client.search(index=index_name, body=query_body)
    if int(response['hits']['total']['value']) == 0:
        logger.info(f'{index_name} 不存在该文章!!  {title}')
        return True
    else:
        logger.info(f'{index_name} 已经存在该文章!!  {title}')
        return False
def screening_date(links_text):
    fb_date, ss_date = None,None
    for link in links_text:
        dt_num = link.get_text()
        if "公布" in dt_num:
            fb_date = dt_num.replace('公布', '')
        if '施行' in dt_num:
            ss_date = dt_num.replace('施行', '')
    return fb_date, ss_date

def screening_document_number(links_text):
    for link in links_text:
        dt_num = link.get_text()
        if "号" in dt_num:
            return dt_num
    return None

def other_msg_calculate(links_other_text):
    shixiao, xiaoli, bumen = None, None, None
    for link in links_other_text:
        text_msg = link.get_text()
        if any(keyword in text_msg for keyword in ['有效', '失效', '修改']):
            shixiao = text_msg
        if any(keyword in text_msg for keyword in ['文件', '法规', '规章', '批复']):
            xiaoli = text_msg
        if any(keyword in text_msg for keyword in ['人民', '政府', '委会', '局', '厅', '法院','其他']):
            bumen = text_msg
    return shixiao, xiaoli, bumen
def extract_titles_and_urls(html_content):
    """
    从 HTML 内容中提取所有标题和 URL，并返回一个字典列表。

    参数:
    html_content (str): 包含 HTML 内容的字符串。

    返回:
    list of dict: 包含标题和 URL 的字典列表。
    """
    count_num = 0
    titles_and_urls = []
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find("div", class_="accompanying-wrap")
    # links = container.find_all('a', attrs={'logfunc': '文章点击', 'target': '_blank', 'flink': 'true'})
    msg_links = container.find_all('div', attrs={'class': 'item'})
    for it in msg_links:
        count_num += 1
        print(count_num)
        link_any = it.find('a', attrs={'logfunc': '文章点击', 'target': '_blank', 'flink': 'true'})
        if not link_any:
            link_any = it.find('a', attrs={'target': '_blank', 'flink': 'true'})
        links_text = it.find_all('span', attrs={'class': 'text'})
        links_other_text = it.find_all('a', attrs={'target': '_blank'}, href=True)
        shixiao, xiaoli, bumen = other_msg_calculate(links_other_text)

        if link_any or links_text:
            fb_date, ss_date = screening_date(links_text)
            biaoti = link_any.get_text().replace("\n", '')
            # 去除首尾的空格
            biaoti = biaoti.strip()
            # 将多个连续的空格替换为单个空格
            biaoti = ' '.join(biaoti.split())
            data_dt = {
                '标题': biaoti,
                '链接': link_any.get('href'),
                '发文字号': screening_document_number(links_text),
                '发布日期': fb_date,
                '实施日期': ss_date,
                '时效性': shixiao,
                '效力级别': xiaoli,
                '发布部门': bumen
            }
            titles_and_urls.append(data_dt)
    # titles_and_urls = [{'标题': link.get_text(), '链接': link.get('href')} for link in links]
    return titles_and_urls


def filter_unwanted_titles(titles_and_urls):
    """
    过滤掉不需要的文章标题。

    参数:
    titles_and_urls (list of dict): 包含标题和 URL 的字典列表。

    返回:
    list of dict: 过滤后的标题和 URL 字典列表。
    """
    filtered_titles_and_urls = []
    for item in titles_and_urls:
        if check_article_exists(item['标题'], 'chl'):
            filtered_titles_and_urls.append(item)
    return filtered_titles_and_urls


def process_html_and_save_to_excel():
    """
    读取 HTML 文件，提取标题和 URL，过滤后保存到 Excel 文件。
    """
    input_file_path = '附件/html.text'
    output_file_path = '附件/法宝法器数据排查/手动获取的文章_价格管理_地方法规_法宝_2.xlsx'

    with open(input_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    titles_and_urls = extract_titles_and_urls(html_content)
    # filtered_titles_and_urls = filter_unwanted_titles(titles_and_urls)

    df = pd.DataFrame(titles_and_urls)
    num_rows = df.shape[0]
    logger.info(f"获取到 {num_rows} 条需要获取的文章")

    df.index.name = '编号'
    df.to_excel(output_file_path, startrow=0, startcol=0)

    logger.info(f"数据已成功保存到 {output_file_path}")
    # new_data_dt = {}
    # # 读取Excel文件
    # df = pd.read_excel("附件/排查_real.xlsx")
    # df1 = pd.read_excel("附件/手动获取的文章.xlsx")
    # # 合并两个DataFrame
    # df_combined = pd.concat([df1, df], ignore_index=True)
    #
    # # 去掉标题重复的行
    # # df_unique = df_combined.drop_duplicates(subset=['标题'])
    # # df_unique = df_combined.drop_duplicates(subset=['链接'])
    # filename = '附件/排查_real.xlsx'
    # with pd.ExcelWriter(filename) as writer:
    #     df_combined.to_excel(writer, startrow=0, startcol=0, index=False)
    # print(f"{filename} 写入完毕！！！")


if __name__ == '__main__':
    process_html_and_save_to_excel()
