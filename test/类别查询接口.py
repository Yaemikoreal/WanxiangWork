from datetime import datetime

import requests


def chuli(key_value, number, key_value1, num):
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
    return [leibeidetail, key_value]


if __name__ == '__main__':
    chuli('长三角地区市场监管领域依法不予实施行政强制措施指导意见', 0,
          '长三角地区市场监管领域依法不予实施行政强制措施指导意见', 0)
