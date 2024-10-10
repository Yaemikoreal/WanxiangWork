import requests

url = 'https://www.pkulaw.com/law/search/RecordSearch'
data = {
    "Menu": "law",
    "Keywords": "",
    "SearchKeywordType": "Title",
    "MatchType": "Exact",
    "RangeType": "Piece",
    "Library": "chl",
    "ClassFlag": "chl",
    "GroupLibraries": "",
    "QueryOnClick": "False",
    "AfterSearch": "False",
    "PreviousLib": "chl",
    "pdfStr": "",
    "pdfTitle": "",
    "IsSynonymSearch": "false",
    "RequestFrom": "btnSearch",
    "LastLibForChangeColumn": "chl",
    "IsSearchProvision": "False",
    "IsCustomSortSearch": "False",
    "CustomSortExpression": "",
    "IsAdv": "False",
    "ClassCodeKey": ",,,,,,",
    "Aggs.RelatedPrompted": "",
    "Aggs.EffectivenessDic": "",
    "Aggs.SpecialType": "",
    "Aggs.IssueDepartment": "",
    "Aggs.TimelinessDic": "",
    "Aggs.Category": "",
    "Aggs.IssueDate": "",
    "GroupByIndex": "2",
    "OrderByIndex": "0",
    "ShowType": "Default",
    "GroupValue": "",
    "TitleKeywords": "",
    "FullTextKeywords": "",
    "Pager.PageIndex": "1",
    "RecordShowType": "List",
    "Pager.PageSize": "100",
    "QueryBase64Request": "",
    "VerifyCodeResult": "",
    "isEng": "chinese",
    "OldPageIndex": "0",
    "newPageIndex": "",
    "IsShowListSummary": "",
    "X-Requested-With": "XMLHttpRequest"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0'
}

response = requests.post(url, json=data, headers=headers)

print(response.status_code)
print(response.json())