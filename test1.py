import re

text = "这是测试文本 渝发改交〔2010〕538号其他文字"
pattern = r'[一-龥]+〔\d{4}〕\d+号'
match = re.search(pattern, text)
match_1 = re.findall(pattern, text)

if match_1:
    print(match_1[0])
else:
    print("None")