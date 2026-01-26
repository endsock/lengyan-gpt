import pdfplumber
from opencc import OpenCC
import os
import sys
from pdf_converter import clean_fontname, get_font_style, detect_layout

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_text_fonts(input_path, target_text, max_pages=None):
    """
    在PDF中查找指定文本并分析其字体信息
    """
    cc = OpenCC('t2s')

    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    print(f"开始分析: {input_path}")
    print(f"查找文本: {target_text}")
    print(f"简体版本: {cc.convert(target_text)}\n")

    try:
        with pdfplumber.open(input_path) as pdf:
            total_pages = len(pdf.pages)
            if max_pages:
                total_pages = min(total_pages, max_pages)

            found = False

            for i in range(total_pages):
                page = pdf.pages[i]
                chars = page.chars

                if not chars:
                    continue

                # 提取页面文本
                page_text = "".join([c['text'] for c in chars])

                # 检查是否包含目标文本
                if target_text in page_text:
                    found = True
                    print(f"在第 {i+1} 页找到目标文本！")
                    print(f"页面布局: {detect_layout(chars)}\n")

                    # 查找目标文本的起始位置
                    start_idx = page_text.index(target_text)
                    end_idx = start_idx + len(target_text)

                    # 分析每个字符的字体
                    print("字符详细信息:")
                    print("-" * 80)

                    for idx in range(start_idx, end_idx):
                        if idx < len(chars):
                            char = chars[idx]
                            text = char['text']
                            fontname = char.get('fontname', 'Unknown')
                            size = char.get('size', 0)

                            # 获取字体样式
                            style = get_font_style(char)
                            clean_name = clean_fontname(fontname)

                            print(f"字符: '{text}'")
                            print(f"  原始字体名: {fontname}")
                            print(f"  清理后字体: {clean_name}")
                            print(f"  字号: {size:.1f}pt")
                            print(f"  字体族: {style['font-family']}")
                            print(f"  字重: {style['font-weight']}")
                            print(f"  位置: x={char['x0']:.1f}, y={char['top']:.1f}")
                            print()

                    print("-" * 80)
                    break

            if not found:
                print(f"在前 {total_pages} 页中未找到目标文本")
                print("提示：PDF可能是繁体字，请尝试搜索繁体版本")

    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    src = r"d:\EBook\fo\楞严经OCR\大佛顶首楞严经讲义[圆瑛法师].pdf"

    # 分析指定文本的字体
    target_text = "如是乃指法之辭，我聞明授受之本"
    analyze_text_fonts(src, target_text, max_pages=60)
