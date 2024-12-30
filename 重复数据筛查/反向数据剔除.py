import pandas as pd
result={'唯一标志': [],'唯一标志pipei':[]}
for year in range(1992, 1995):
    data=pd.read_excel(fr'E:\JXdata\Python\wan\测试\重复数据表\重复数据_{year}.xlsx',dtype=str)
    # print(data)
    # data2=pd.read_excel('根据文号匹配1992-1995.xlsx',dtype=str)
    # for dddd,row in data.iterrows():
    # data_list1=list(data1['唯一标志'])+list(data2['唯一标志'])
    # data_list2=list(data1['唯一标志pipei'])+list(data2['唯一标志pipei'])
    data_list1 = list(data['唯一标志'])
    data_list2 = list(data['唯一标志pipei'])
    result_dict =list(zip(data_list1, data_list2))
    # 新建一个集合用于存储反向顺序对应的值
    # 新建一个集合用于存储反向顺序对应的值
    reversed_pairs = set()
    processed_items = set()  # 用于跟踪已处理的元组
    for item in result_dict:
        a1, a2 = item
        # 判断a2, a1是否在列表中存在且当前元组未被处理过
        if (a2, a1) in result_dict and item not in processed_items:
            result['唯一标志'].append(a1)
            result['唯一标志pipei'].append(a2)
            reversed_pairs.add((a1, a2))
            processed_items.add((a2, a1))  # 将反向顺序的元组标记为已处理

    # 只返回其中一个符合条件的元素
    print(reversed_pairs)
    result_df1 = pd.DataFrame(result)
    result_df1.to_excel(fr'E:\JXdata\Python\wan\测试\反向数据\反向数据{year}.xlsx', index=False)
