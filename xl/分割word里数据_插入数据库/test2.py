# 导入必要的库
import re


def split_text_by_marker(file_path):
    # 读取文件
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # 定义分割标记
    marker = "【条文主旨】"

    # 使用正则表达式分割文本
    # 正则表达式解释：
    # .*? 非贪婪匹配任意字符直到遇到下一个匹配项
    # re.DOTALL 让 . 匹配所有字符，包括换行符
    segments = re.split(f"{marker}.*?\n\n", content, flags=re.DOTALL)

    # 处理分割结果，去除首尾多余的文本
    processed_segments = []
    for segment in segments:
        if segment:
            processed_segment = segment.strip()
            if processed_segment.startswith(marker):
                processed_segment = processed_segment[len(marker):].strip()
            processed_segments.append(processed_segment)

    return processed_segments


# 示例使用
file_path = r'D:\work\WanxiangWork\xl\abc.txt'  # 替换为实际文件路径
segments = split_text_by_marker(file_path)

# 输出分割后的段落
for i, segment in enumerate(segments):
    print(f"Segment {i + 1}:")
    print(segment)
    print("-" * 50)