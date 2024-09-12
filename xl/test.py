import re


def space_clear_html(space_clear_html):
    # 查找第一个<p>标签的位置，并保留其后面的所有内容
    match = re.search(r'<p', space_clear_html)
    if match:
        # 取从<p>开始到结束的所有内容
        cleared_data = space_clear_html[match.start():]
        return cleared_data
    else:
        # 如果没有找到<p>标签，返回原字符串或空字符串
        return ""


# 示例数据
data_dt = '<div class="zcwjk-xlcon"><div id="a1"></div><p></p><p></p><p style="text-align:center">重庆市审计局关于废止《重庆市内部审计</p><p style="text-align:center">业务工作规程（试行）》的通知</p><p style="text-align:center"><span>渝审发〔2023〕65号</span></p><p></p><p>各区县（自治县）审计局，两江新区、万盛经开区审计局，市属各国家机关、国有企业、事业单位内部审计机构：</p><p>经研究，重庆市审计局决定废止《重庆市审计局关于印发重庆市内部审计业务工作规程（试行）的通知》（渝审发〔2015〕8号）。本决定自发布之日起施行。</p><p></p><div style="text-align:right"> 重庆市审计局</div><div style="text-align:right">                                       2023年12月11日</div></div>'

# 调用函数
cleaned_html = space_clear_html(data_dt)
print(cleaned_html)