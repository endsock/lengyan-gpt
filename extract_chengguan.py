import re
import os

# 输入文件
input_file = "成观法师大佛顶首楞严经义贯1769356465.md"
# 输出目录
output_dir = "chengguan_doc"

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 读取文件内容
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()

# 正则表达式：匹配 **【...】** 格式，排除"注释"、"义贯"、"诠论"
pattern = r'\*\*【(?!注释|义贯|诠论)[\s\S]+?】\*\*'

# 查找所有匹配
matches = re.findall(pattern, content)

# 提取并清理内容
extracted_texts = []
excluded_heading_line = re.compile(r"(?m)^\s*\*\*【(?:注释|义贯|诠论)】\*\*\s*$")
for match in matches:
    # 清掉可能被跨行匹配带进来的 **【注释】** / **【义贯】** / **【诠论】** 行
    cleaned = excluded_heading_line.sub("", match)

    # 合并跨行断开的粗体标记：如 **...**\n\n**...**（可能带缩进/多空行）
    cleaned = re.sub(r'\*\*\s*\n+\s*\*\*', '', cleaned)

    # 将 **【...】** 块内容折叠为一行：去掉换行及其两侧空白
    cleaned = re.sub(r'\s*\n+\s*', '', cleaned)

    # 规整空行（理论上块内已无换行；保留以防其他情况）
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    if cleaned:
        extracted_texts.append(cleaned)

# 合并所有提取的文本
output_text = "\n\n".join(extracted_texts)

# 输出文件
output_file = os.path.join(output_dir, "sutra_text.md")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(output_text)

print(f"Extraction complete!")
print(f"Total extracted: {len(extracted_texts)} blocks")
print(f"Output file: {output_file}")
