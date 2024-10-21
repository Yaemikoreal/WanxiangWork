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


def extract_titles_and_urls(html_content):
    """
    从 HTML 内容中提取所有标题和 URL，并返回一个字典列表。

    参数:
    html_content (str): 包含 HTML 内容的字符串。

    返回:
    list of dict: 包含标题和 URL 的字典列表。
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    container = soup.find("div", class_="accompanying-wrap")
    links = container.find_all('a', attrs={'logfunc': '文章点击', 'target': '_blank', 'flink': 'true'})

    titles_and_urls = [{'标题': link.get_text(), '链接': link.get('href')} for link in links]
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
    output_file_path = '附件/手动获取的文章.xlsx'

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


if __name__ == '__main__':
    process_html_and_save_to_excel()
