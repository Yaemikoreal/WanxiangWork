import requests
import json


headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\""
}
cookies = {
    "SESSION": "OTgxYTYyNTctMDc1ZS00OTZiLTg5ZmUtNjhlNjk4YjUzZjVl",
    "_trs_uv": "m0ymru74_3964_djdi",
    "userInfo": "",
    "_trs_user": "",
    "_trs_gv": "g_m0ymru74_3964_djdi",
    "_trs_ua_s_1": "m1g21f3f_3486_68sj",
    "arialoadData": "true",
    "ariawapChangeViewPort": "false"
}
url = "https://wap.cq.gov.cn/irs/front/search"
data = {
    "id": "7",
    "tenantId": "7",
    "searchWord": "全体会议决议",
    "dataTypeId": "7",
    "pageNo": 3,
    "pageSize": 10,
    "orderBy": "related",
    "searchBy": "title",
    "appendixType": "",
    "granularity": "ALL",
    "beginDateTime": "",
    "endDateTime": "",
    "isSearchForced": 0,
    "filters": [],
    "sign": "ea9dfdbd-309b-4830-99aa-87f227622dcf",
    "pager": {
        "pageNo": 22
    },
    "searchInfo": {},
    "dataTypes": [],
    "configTenantId": "7",
    "historySearchWords": [
        "全体会议决议"
    ],
    "operationType": "search",
    "seniorBox": 0,
    "isDefaultAdvanced": 0,
    "isAdvancedSearch": 0,
    "advancedFilters": [],
    "customFilters": [],
    "areaCode": ""
}
data = json.dumps(data, separators=(',', ':'))
response = requests.post(url, headers=headers,  data=data)

print(response.text)
print(response)