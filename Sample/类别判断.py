# -*- coding: utf-8 -*-
from datetime import datetime
import requests
import jieba
import re

def chuli(key_value,number,key_value1,num):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://lawdoo.com',
        'Pragma': 'no-cache',
        'Referer': 'https://lawdoo.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76',
        'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    try:
        while key_value:
            # print(key_value)
            timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
            params = {
                'lib': 'lar',
                'menuConditions': '0,0,0,0',
                'conditions': f'{key_value},,,0;0,0,-,-,-,0;0,0;0,0;0',
                'a': f'{timestamp}',
                'isPrecision': 'true',
                '_': f'{timestamp}',
            }
            response = requests.get('https://api.lawdoo.com/api/FD/GetLeftMenuList', params=params, headers=headers)
            data_list1 = response.json()
            if 'z_menuList' in data_list1:
                data_list = response.json()['z_menuList'][1]
                break
            else:
                number += 1
                key_value = key_value[number:-number]
        # max_data = max(data_list, key=lambda x: x['sum'])
        max_data = sorted(data_list, key=lambda x: x['sum'], reverse=True)[num]
    except:
        key_value = " ".join(key_value1)
        while key_value:
            # print(key_value)
            timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
            params = {
                'lib': 'lar',
                'menuConditions': '0,0,0,0',
                'conditions': f'{key_value},,,0;0,0,-,-,-,0;0,0;0,0;0',
                'a': f'{timestamp}',
                'isPrecision': 'true',
                '_': f'{timestamp}',
            }
            response = requests.get('https://api.lawdoo.com/api/FD/GetLeftMenuList', params=params, headers=headers)
            data_list1 = response.json()
            if 'z_menuList' in data_list1:
                data_list = response.json()['z_menuList'][1]
                break
            else:
                number += 1
                key_value = key_value[number + 2:-number - 1]
        max_data = sorted(data_list, key=lambda x: x['sum'], reverse=True)[num]
    # print(key_value)
    timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
    paramdetail = {
        'lib': 'lar',
        'menuConditions': f'0,{max_data["ID"]},0,0',
        'conditions': f'{key_value},,,0;0,0,-,-,-,0;0,0;0,0;{max_data["ID"]}',
        'a': f'{timestamp}',
        'isPrecision': 'true',
        '_': f'{timestamp}',
    }
    responsedetail = requests.get('https://api.lawdoo.com/api/FD/GetLeftMenuList', params=paramdetail,
                                  headers=headers)
    # print(responsedetail.json()['z_menuList'])
    leibeidetail = [(i['Value'], i['sum'], i['ID']) for i in responsedetail.json()['z_menuList'][1]][0][-1]
    return [leibeidetail,key_value]

def get_catagroy(value):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://lawdoo.com',
        'Pragma': 'no-cache',
        'Referer': 'https://lawdoo.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76',
        'sec-ch-ua': '"Chromium";v="118", "Microsoft Edge";v="118", "Not=A?Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    # key_value1=keyjieba(value)
    key_value1 = re.sub("[^a-zA-Z0-9\u4E00-\u9FA5]",'',value.split('印发')[-1].split('关于')[-1].split('改革委')[-1].split('转发')[-1])
    number=0
    key_value=key_value1
    # print(key_value)

    max_attempts = 5
    attempt = 0
    try:
        while attempt < max_attempts:
            try:
                leibeidetail, key_value = chuli(key_value, number, key_value1, attempt)
                break
            except IndexError:
                attempt += 1
    except:
        leibeidetail='00301'
        key_value=key_value

    if attempt == max_attempts:
        leibeidetail, key_value = chuli(key_value, number, key_value1, attempt)

    if leibeidetail=='00301':
        try:
            leibeidetail = chuli(key_value, number, key_value1, 2)[0]
            key_value = chuli(key_value, number, key_value1, 2)[1]
        except:
            leibeidetail=leibeidetail
            key_value=key_value
    # print(key_value,leibeidetail)
    if len(leibeidetail)>5:
        leibeidet=leibeidetail[:3]+';'+leibeidetail[:5]+';'+leibeidetail
    elif len(leibeidetail)==5:
        leibeidet=leibeidetail[:3]+';'+leibeidetail
    else:
        leibeidet=leibeidetail
    if len(key_value.strip())<4:
        leibeidet='003;00301'
    # print(value,leibeidet)
    return leibeidet

# # liii=['青海省财政厅国家税务总局青海省税务局关于进一步实施小微企业“六税两费”减免政策通知','青海省财政厅关于印发《关于实施支持农牧业转移人口市民化若干财政政策的实施意见》的通知','青海省财政厅国家税务总局青海省税务局中国人民银行西宁中心支行关于废止青财预字〔2017〕2200号文件的通知','青海省财政厅青海省公安厅中国人民银行西宁中心支行关于印发《青海省开展异地缴纳非现场交通违法罚款工作实施方案》的通知','青海省财政厅青海省发展和改革委员会《关于修订青海省服务业发展引导资金管理办法的通知》']
# liii=['重庆市涪陵区司法局关于印发《贯彻实施〈中华人民共和国行政复议法〉工作方案》的通知','重庆市涪陵区人民政府办公室 关于印发重庆市涪陵区城市内涝处置应急预案的通知','重庆市涪陵区人民政府办公室 关于印发涪陵区园区开发区行政事权改革实施方案的通知','重庆市渝中区统计局关于开展2024年劳动工资季报工作的通知','广东省市场监督管理局办公室关于开展2024年经营环节食品相关产品监督抽检工作的通知','广东省生态环境厅广东省市场监督管理局关于批准下达推动大规模设备更新和消费品以旧换新相关地方标准制修订计划(第三批)的通知','广东省市场监督管理局关于征集标准化领域专家的通知','广东省食品药品安全与高质量发展委员会办公室 广东省公安厅 广东省农业农村厅 广东省市场监督管理局关于印发2024年广东省严厉打击肉类产品违法犯罪专项整治行动方案的通知','陕西省市场监督管理局关于印发《陕西省检验检测领域突出问题专项治理实施方案》的通知','陕西省市场监督管理局关于征集陕西省市场监管局质量发展专家库候选专家的通知','内蒙古自治区市场监督管理局关于责令限期履行相关义务的通知','内蒙古自治区市场监督管理局、内蒙古自治区知识产权局关于公布首批知识产权行政裁决所的通知','内蒙古自治区市场监督管理局关于举办2024年度工程系列计量、标准化、产品质量、特种设备专业技术人员继续教育专业课网络学习的通知','湖南省医疗保障局、湖南省人力资源和社会保障厅、湖南省卫生健康委员会关于做好“第一、三批国家组织药品集中带量采购协议期满接续”和“易短缺和急抢救药联盟”集中带量采购中选结果执行工作的通知']
# for i in liii:
#     # print(i)
#     get_catagroy(i)