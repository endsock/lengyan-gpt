import pdfplumber
from opencc import OpenCC
import os

def detect_layout(chars):
    """
    检测PDF是横排还是竖排
    返回 'horizontal' 或 'vertical'
    """
    if len(chars) < 10:
        return 'horizontal'

    # 统计不同的x坐标和y坐标数量
    unique_x = len(set([round(c['x0'], 1) for c in chars]))
    unique_y = len(set([round(c['top'], 1) for c in chars]))

    # 如果X坐标数量远小于Y坐标数量，说明是竖排（列少，每列字符多）
    # 如果Y坐标数量远小于X坐标数量，说明是横排（行少，每行字符多）
    if unique_x < unique_y * 0.5:
        return 'vertical'
    else:
        return 'horizontal'

def clean_fontname(fontname):
    """
    清理PDF字体名称，移除随机前缀
    例如: "ABCDE+SimSun" -> "SimSun"
    """
    if not fontname:
        return None

    # 移除随机前缀（通常是6位大写字母+加号）
    if '+' in fontname:
        fontname = fontname.split('+', 1)[1]

    # 移除常见的后缀
    fontname = fontname.replace('-Bold', '').replace('-Italic', '')
    fontname = fontname.replace('-Regular', '').replace('-Medium', '')

    return fontname

def get_font_style(char):
    """
    从字符提取字体样式信息
    返回包含 font-family, font-size, font-weight 的字典
    """
    fontname = char.get('fontname', '')
    size = char.get('size', 12)

    # 清理字体名称
    clean_name = clean_fontname(fontname)

    # 检测粗体
    font_weight = 'normal'
    if fontname:
        fontname_lower = fontname.lower()
        if any(x in fontname_lower for x in ['bold', 'heavy', 'black', 'bd']):
            font_weight = 'bold'

    # 字体映射（PDF字体名 -> Web安全字体）
    font_map = {
        'SimSun': '"SimSun", "宋体", serif',
        'SimHei': '"SimHei", "黑体", sans-serif',
        'KaiTi': '"KaiTi", "楷体", serif',
        'FangSong': '"FangSong", "仿宋", serif',
        'FZShuSong': '"FZShuSong", "方正书宋", serif',
        'FZKai': '"FZKai", "方正楷体", serif',
        'FZSong': '"FZSong", "方正宋体", serif',
        'STSong': '"STSong", "华文宋体", serif',
        'STKaiti': '"STKaiti", "华文楷体", serif',
        'STHeiti': '"STHeiti", "华文黑体", sans-serif',
        'STFangsong': '"STFangsong", "华文仿宋", serif',
        'Arial': 'Arial, sans-serif',
        'Times': '"Times New Roman", Times, serif',
        'Courier': '"Courier New", Courier, monospace',
    }

    font_family = font_map.get(clean_name, f'"{clean_name}", "SimSun", serif')

    return {
        'font-family': font_family,
        'font-size': f'{size:.1f}pt',
        'font-weight': font_weight
    }

def convert_pdf_to_html(input_path, output_path, max_pages=None, skip_pages=2):
    """
    解析PDF，将繁体转换为简体，输出为HTML格式，保留文字格式。
    支持横排和竖排布局。

    参数:
        skip_pages: 跳过前N页，默认跳过前2页
    """
    cc = OpenCC('t2s')

    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    print(f"开始处理: {input_path}")
    print(f"跳过前 {skip_pages} 页")

    try:
        with pdfplumber.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            if max_pages:
                total_pages = min(total_pages, max_pages)

            html_content = []

            # HTML 头部
            html_content.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>楞严经讲义 - 简体版</title>
    <style>
        body {
            font-family: "Microsoft YaHei", "SimSun", serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            background-color: #f0f2f5;
            color: #333;
            line-height: 1.8;
        }
        .page {
            background-color: white;
            padding: 50px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-radius: 4px;
            min-height: 1000px;
        }
        .page-number {
            text-align: center;
            color: #aaa;
            font-size: 13px;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            clear: both;
        }
        .text-line {
            margin-bottom: 8px;
            min-height: 1.2em;
        }
        strong {
            font-weight: bold;
            color: #000;
        }
        /* 字体样式类 */
        .font-normal {
            font-weight: normal;
        }
        .font-bold {
            font-weight: bold;
        }
    </style>
</head>
<body>
""")

            for i in range(skip_pages, total_pages):
                page = pdf.pages[i]
                print(f"处理进度: {i+1}/{total_pages} 页")

                chars = page.chars
                if not chars:
                    html_content.append(f'<div class="page"><p class="page-number">第 {i+1} 页（无文字内容）</p></div>\n')
                    continue

                # 过滤：只保留16pt和13pt的字符（允许±0.5pt的误差）
                filtered_chars = [c for c in chars if 12.5 <= c['size'] <= 13.5 or 15.5 <= c['size'] <= 16.5]

                if not filtered_chars:
                    html_content.append(f'<div class="page"><p class="page-number">第 {i+1} 页（无匹配字号内容）</p></div>\n')
                    continue

                # 检测布局
                layout = detect_layout(filtered_chars)
                unique_x = len(set([round(c['x0'], 1) for c in filtered_chars]))
                unique_y = len(set([round(c['top'], 1) for c in filtered_chars]))
                print(f"  X坐标数:{unique_x}, Y坐标数:{unique_y}, 布局:{layout}")

                html_content.append(f'<div class="page">\n')

                if layout == 'vertical':
                    # 竖排布局：按列组织
                    # 先按x坐标排序
                    sorted_chars = sorted(filtered_chars, key=lambda c: c['x0'])

                    columns = []
                    if sorted_chars:
                        current_column = [sorted_chars[0]]
                        for j in range(1, len(sorted_chars)):
                            char = sorted_chars[j]
                            prev_char = sorted_chars[j-1]

                            # 如果x坐标差异小于字号的一半，视为同一列
                            tolerance = prev_char['size'] * 0.5
                            if char['x0'] - prev_char['x0'] < tolerance:
                                current_column.append(char)
                            else:
                                columns.append(current_column)
                                current_column = [char]
                        columns.append(current_column)

                    # 台湾竖排文本：从右向左排列
                    for column in reversed(columns):
                        # 列内按y坐标排序（从上到下）
                        column_chars = sorted(column, key=lambda c: c['top'])

                        column_text = "".join([c['text'] for c in column_chars]).strip()
                        if not column_text:
                            continue

                        line_html = '<div class="text-line">'
                        last_y = -1
                        current_style = None
                        span_text = ""

                        for idx, char in enumerate(column_chars):
                            text = char['text']

                            # 如果y坐标间距较大，补空格
                            if last_y != -1 and (char['top'] - last_y) > char['size'] * 1.5:
                                if span_text:
                                    # 先输出当前span
                                    simplified = cc.convert(span_text)
                                    if current_style:
                                        style_str = '; '.join([f'{k}: {v}' for k, v in current_style.items()])
                                        line_html += f'<span style="{style_str}">{simplified}</span>'
                                    else:
                                        line_html += simplified
                                    span_text = ""
                                line_html += " "

                            # 获取当前字符的字体样式
                            char_style = get_font_style(char)

                            # 如果字体样式改变，输出之前的文本并开始新的span
                            if current_style != char_style:
                                if span_text:
                                    simplified = cc.convert(span_text)
                                    if current_style:
                                        style_str = '; '.join([f'{k}: {v}' for k, v in current_style.items()])
                                        line_html += f'<span style="{style_str}">{simplified}</span>'
                                    else:
                                        line_html += simplified
                                    span_text = ""
                                current_style = char_style

                            span_text += text
                            last_y = char['bottom']

                        # 输出最后一段文本
                        if span_text:
                            simplified = cc.convert(span_text)
                            if current_style:
                                style_str = '; '.join([f'{k}: {v}' for k, v in current_style.items()])
                                line_html += f'<span style="{style_str}">{simplified}</span>'
                            else:
                                line_html += simplified

                        line_html += '</div>\n'
                        html_content.append(line_html)

                else:
                    # 横排布局：按行组织
                    sorted_chars = sorted(filtered_chars, key=lambda c: c['top'])

                    lines = []
                    if sorted_chars:
                        current_line = [sorted_chars[0]]
                        for j in range(1, len(sorted_chars)):
                            char = sorted_chars[j]
                            prev_char = sorted_chars[j-1]

                            tolerance = prev_char['size'] * 0.5
                            if char['top'] - prev_char['top'] < tolerance:
                                current_line.append(char)
                            else:
                                lines.append(current_line)
                                current_line = [char]
                        lines.append(current_line)

                    for line in lines:
                        line_chars = sorted(line, key=lambda c: c['x0'])
                        line_text = "".join([c['text'] for c in line_chars]).strip()
                        if not line_text:
                            continue

                        line_html = '<div class="text-line">'
                        last_x = -1
                        current_style = None
                        span_text = ""

                        for idx, char in enumerate(line_chars):
                            text = char['text']

                            if last_x != -1 and (char['x0'] - last_x) > char['size'] * 1.5:
                                if span_text:
                                    # 先输出当前span
                                    simplified = cc.convert(span_text)
                                    if current_style:
                                        style_str = '; '.join([f'{k}: {v}' for k, v in current_style.items()])
                                        line_html += f'<span style="{style_str}">{simplified}</span>'
                                    else:
                                        line_html += simplified
                                    span_text = ""
                                line_html += " "

                            # 获取当前字符的字体样式
                            char_style = get_font_style(char)

                            # 如果字体样式改变，输出之前的文本并开始新的span
                            if current_style != char_style:
                                if span_text:
                                    simplified = cc.convert(span_text)
                                    if current_style:
                                        style_str = '; '.join([f'{k}: {v}' for k, v in current_style.items()])
                                        line_html += f'<span style="{style_str}">{simplified}</span>'
                                    else:
                                        line_html += simplified
                                    span_text = ""
                                current_style = char_style

                            span_text += text
                            last_x = char['x1']

                        # 输出最后一段文本
                        if span_text:
                            simplified = cc.convert(span_text)
                            if current_style:
                                style_str = '; '.join([f'{k}: {v}' for k, v in current_style.items()])
                                line_html += f'<span style="{style_str}">{simplified}</span>'
                            else:
                                line_html += simplified

                        line_html += '</div>\n'
                        html_content.append(line_html)

                html_content.append(f'<p class="page-number">第 {i+1} 页</p>\n')
                html_content.append('</div>\n')

            # HTML 尾部
            html_content.append("""
</body>
</html>
""")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(html_content)

            print(f"\n转换成功！\n输出文件：{output_path}")

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

def convert_pdf_to_md(input_path, output_path, max_pages=None, skip_pages=2):
    """
    解析PDF，将繁体转换为简体，输出为Markdown格式。
    根据字号区分经文(16pt)和讲义(13pt)。

    参数:
        skip_pages: 跳过前N页，默认跳过前2页
    """
    cc = OpenCC('t2s')

    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    print(f"开始转换 Markdown: {input_path}")
    print(f"跳过前 {skip_pages} 页")

    try:
        with pdfplumber.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            if max_pages:
                total_pages = min(total_pages, max_pages)

            md_content = []
            md_content.append("# 楞严经讲义 - 简体版\n\n")

            for i in range(skip_pages, total_pages):
                page = pdf.pages[i]
                print(f"处理进度: {i+1}/{total_pages} 页")

                chars = page.chars
                if not chars:
                    continue

                # 过滤：只保留16pt和13pt的字符（允许±0.5pt的误差）
                filtered_chars = [c for c in chars if 12.5 <= c['size'] <= 13.5 or 15.5 <= c['size'] <= 16.5]

                if not filtered_chars:
                    continue

                # 检测布局
                layout = detect_layout(filtered_chars)

                md_content.append(f"<!-- 第 {i+1} 页 -->\n\n")

                if layout == 'vertical':
                    # 竖排布局：按列组织
                    sorted_chars = sorted(filtered_chars, key=lambda c: c['x0'])
                    columns = []
                    if sorted_chars:
                        current_column = [sorted_chars[0]]
                        for j in range(1, len(sorted_chars)):
                            char = sorted_chars[j]
                            prev_char = sorted_chars[j-1]
                            tolerance = prev_char['size'] * 0.5
                            if char['x0'] - prev_char['x0'] < tolerance:
                                current_column.append(char)
                            else:
                                columns.append(current_column)
                                current_column = [char]
                        columns.append(current_column)

                    for column in reversed(columns):
                        column_chars = sorted(column, key=lambda c: c['top'])

                        # 按字号分组处理列内文本
                        if not column_chars:
                            continue

                        current_size = round(column_chars[0]['size'], 1)
                        current_text = ""

                        for char in column_chars:
                            size = round(char['size'], 1)
                            text = char['text']

                            if size != current_size:
                                # 输出当前组
                                simplified = cc.convert(current_text).strip()
                                if simplified:
                                    if current_size >= 15.5: # 经文 (16pt)
                                        md_content.append(f"**{simplified}**")
                                    elif current_size >= 12.5: # 讲义 (13pt)
                                        md_content.append(simplified)
                                    else:
                                        md_content.append(simplified)

                                current_size = size
                                current_text = text
                            else:
                                current_text += text

                        # 输出最后一组
                        simplified = cc.convert(current_text).strip()
                        if simplified:
                            if current_size >= 15.5:
                                md_content.append(f"**{simplified}**\n\n")
                            else:
                                md_content.append(f"{simplified}\n\n")
                else:
                    # 横排布局
                    sorted_chars = sorted(filtered_chars, key=lambda c: c['top'])
                    lines = []
                    if sorted_chars:
                        current_line = [sorted_chars[0]]
                        for j in range(1, len(sorted_chars)):
                            char = sorted_chars[j]
                            prev_char = sorted_chars[j-1]
                            tolerance = prev_char['size'] * 0.5
                            if char['top'] - prev_char['top'] < tolerance:
                                current_line.append(char)
                            else:
                                lines.append(current_line)
                                current_line = [char]
                        lines.append(current_line)

                    for line in lines:
                        line_chars = sorted(line, key=lambda c: c['x0'])
                        if not line_chars:
                            continue

                        current_size = round(line_chars[0]['size'], 1)
                        current_text = ""

                        for char in line_chars:
                            size = round(char['size'], 1)
                            text = char['text']

                            if size != current_size:
                                simplified = cc.convert(current_text).strip()
                                if simplified:
                                    if current_size >= 15.5:
                                        md_content.append(f"**{simplified}**")
                                    else:
                                        md_content.append(simplified)
                                current_size = size
                                current_text = text
                            else:
                                current_text += text

                        simplified = cc.convert(current_text).strip()
                        if simplified:
                            if current_size >= 15.5:
                                md_content.append(f"**{simplified}**\n\n")
                            else:
                                md_content.append(f"{simplified}\n\n")

                md_content.append(f"\n---\n*第 {i+2} 页*\n\n")

            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(md_content)

            print(f"\nMarkdown 转换成功！\n输出文件：{output_path}")

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    src = r"d:\EBook\fo\楞严经OCR\大佛顶首楞严经讲义[圆瑛法师].pdf"

    # 测试 Markdown 转换
    dst_md = os.path.join(os.getcwd(), "楞严经讲记_测试.md")
    convert_pdf_to_md(src, dst_md)
