import time
import pandas as pd
import re
from functools import partial
import datetime
from multiprocessing.dummy import Pool
from elasticsearch import Elasticsearch

es = Elasticsearch(
    ['http://10.0.0.1:8041'],
    http_auth=('elastic', 'Cdxb1998123!@#')
)


def pandaun(title, titlepipei, ziduan):
    aaaa = (ziduan in title and ziduan not in str(titlepipei)) or (ziduan not in title and ziduan in str(titlepipei))
    return aaaa


# print(pandaun('aaa','aaa','aaa'))
def get_copy_data(year):
    print(year)
    data = pd.read_excel(rf'E:\JXdata\Python\wan\测试\全部数据\全部数据{year}.xlsx', dtype=str)
    resalu = {'唯一标志': [], '标题': [], '发文字号': [], '发布日期': [], 'urlwu': [], '部门': [], '唯一标志pipei': [],
              '标题pipei': [], '发文字号pipei': [], '发布日期pipei': [], 'urlwupipei': [], '部门pipei': []}
    resalu_cuo = {'唯一标志': [], '标题': [], '发文字号': [], '发布日期': [], 'urlwu': [], '部门': [],
                  '唯一标志pipei': [], '标题pipei': [], '发文字号pipei': [], '发布日期pipei': [], 'urlwupipei': [],
                  '部门pipei': []}
    numdd = 0
    for index, row in data.iterrows():
        numdd += 1
        print('{}_第{}条'.format(year, numdd))
        try:
            title = row['标题']
            # aaa=re.findall('(\(\d{0,4}修[订|正]\))',title)
            # if aaa:
            #     titlegeng=title.split(aaa[0])[0]
            titlegeng = title.split('关于')[-1].replace('[失效]', '')  #.split('印发')[-1]
            发文字号 = str(row['发文字号'])
            chean_textchean_text = re.sub(r'[^0-9]', '',
                                          发文字号)  #.split('关于')[-1] = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)  # .split('关于')[-1]
            # print(chean_textchean_text)
            body = {
                "query": {
                    "match_phrase": {
                        '标题': titlegeng
                    }
                }, "size": 100
            }
            resp = es.search(index='lar', body=body)
            list11 = resp['hits']['hits']
            for lll in list11:
                # try:
                try:
                    lll_fawnezi = str(lll['_source']['发文字号'])
                except:
                    lll_fawnezi = ''
                try:
                    departments = re.findall(';(\d{3});',
                                             str(lll['_source']['发布部门']).replace("', '", ';').replace("['",
                                                                                                          '').replace(
                                                 "']", ''))[0]
                except:
                    departments = ''
                try:
                    xindedate = str(lll['_source']['发布日期'])
                except:
                    xindedate = ''
                chean_lll_fawnezi = re.sub(r'[^0-9]', '', lll_fawnezi)
                titlepipeee = lll['_source']['标题']
                if len(chean_lll_fawnezi) > 0:
                    # print(xindedate)
                    # print(str(row['唯一标志'])[:4])
                    if chean_lll_fawnezi == chean_textchean_text and lll['_id'] != row['唯一标志']:
                        if str(row['发布日期'])[:4] == str(xindedate)[:4] and str(row['部门']) == departments:
                            # if ('贯彻' in title and '贯彻' not in str(lll['_source']['标题'])) or ('贯彻' not in title and '贯彻' in str(lll['_source']['标题'])) or ('转' in title and '转' not in str(lll['_source']['标题'])) or ('转' not in title and '转' in str(lll['_source']['标题'])) or ('批准' not in title and '批准' in str(lll['_source']['标题'])) or ('批准' in title and '批准' not in str(lll['_source']['标题'])):
                            #     pass
                            if pandaun(title, titlepipeee, '贯彻') or pandaun(title, titlepipeee, '转') or pandaun(
                                    title, titlepipeee, '批准') or pandaun(title, titlepipeee, '关于修改'):
                                pass
                            else:
                                if ('市' in str(title[:3]) and str(title[:2]) not in str(lll['_source']['标题'])) or (
                                        '市' in str(str(lll['_source']['标题'])[:3]) and str(
                                        str(lll['_source']['标题'])[:2]) not in str(title)):
                                    pass
                                else:
                                    resalu['唯一标志'].append(row['唯一标志'])
                                    resalu['标题'].append(title)
                                    resalu['发文字号'].append(row['发文字号'])
                                    resalu['发布日期'].append(row['发布日期'])
                                    resalu['urlwu'].append(
                                        f"https://lawdoo.com/Home/NewsShow/{row['唯一标志']}/lar/-1/,,,0;0,0,-,-,-,0;0,0;0,0;0/True")
                                    resalu['部门'].append(row['部门'])
                                    resalu['唯一标志pipei'].append(lll['_id'])
                                    resalu['标题pipei'].append(str(lll['_source']['标题']))
                                    resalu['发文字号pipei'].append(lll_fawnezi)
                                    resalu['发布日期pipei'].append(xindedate)
                                    resalu['urlwupipei'].append(
                                        f"https://lawdoo.com/Home/NewsShow/{lll['_id']}/lar/-1/,,,0;0,0,-,-,-,0;0,0;0,0;0/True")
                                    resalu['部门pipei'].append(departments)
                                    print('文号', row['唯一标志'])
                else:
                    if row['发布日期'] == xindedate and lll['_id'] != row['唯一标志'] and str(
                            row['部门']) == departments:
                        if pandaun(title, titlepipeee, '贯彻') or pandaun(title, titlepipeee, '转') or pandaun(title,
                                                                                                               titlepipeee,
                                                                                                               '批准') or pandaun(
                                title, titlepipeee, '关于修改'):
                            pass
                        else:
                            if ('市' in str(title[:3]) and str(title[:2]) not in str(lll['_source']['标题'])) or (
                                    '市' in str(str(lll['_source']['标题'])[:3]) and str(
                                    str(lll['_source']['标题'])[:2]) not in str(title)):
                                pass
                            else:
                                resalu['唯一标志'].append(row['唯一标志'])
                                resalu['标题'].append(title)
                                resalu['发文字号'].append(row['发文字号'])
                                resalu['发布日期'].append(row['发布日期'])
                                resalu['urlwu'].append(
                                    f"https://lawdoo.com/Home/NewsShow/{row['唯一标志']}/lar/-1/,,,0;0,0,-,-,-,0;0,0;0,0;0/True")
                                resalu['部门'].append(row['部门'])
                                resalu['唯一标志pipei'].append(lll['_id'])
                                resalu['标题pipei'].append(str(lll['_source']['标题']))
                                resalu['发文字号pipei'].append(lll_fawnezi)
                                resalu['发布日期pipei'].append(xindedate)
                                resalu['urlwupipei'].append(
                                    f"https://lawdoo.com/Home/NewsShow/{lll['_id']}/lar/-1/,,,0;0,0,-,-,-,0;0,0;0,0;0/True")
                                resalu['部门pipei'].append(departments)
                                print(row['唯一标志'])
                # except:
                #     resalu_cuo['唯一标志'].append(row['唯一标志'])
        except:
            time.sleep(10)
            pass
    # result_df = pd.DataFrame(resalu_cuo)
    # result_df.to_excel(fr'E:\fql\监控更新\重复数据处理\重复数据表\重复数据_{year}.xlsx', index=False)
    result_df1 = pd.DataFrame(resalu)
    if not result_df1.empty:
        result_df1.to_excel(rf'E:\JXdata\Python\wan\测试\重复数据表\重复数据_{year}.xlsx', index=False)


def run():
    url_list = range(1992, 1995)
    partial_function = partial(get_copy_data)
    pool = Pool(3)
    pool.map(partial_function, url_list)


run()
