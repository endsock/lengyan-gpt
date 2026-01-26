import pdfplumber
import os

def debug_pdf(input_path, page_num=1):
    """调试：查看PDF页面的字符坐标分布"""
    if not os.path.exists(input_path):
        print(f"错误：找不到文件 {input_path}")
        return

    with pdfplumber.open(input_path) as pdf:
        page = pdf.pages[page_num - 1]
        chars = page.chars

        print(f"第 {page_num} 页共有 {len(chars)} 个字符")
        print("\n前20个字符的坐标信息:")
        print(f"{'字符':<4} {'x0':<8} {'x1':<8} {'top':<8} {'bottom':<8} {'size':<6} {'font'}")
        print("-" * 80)

        for i, char in enumerate(chars[:20]):
            print(f"{char['text']:<4} {char['x0']:<8.1f} {char['x1']:<8.1f} {char['top']:<8.1f} {char['bottom']:<8.1f} {char['size']:<6.1f} {char.get('fontname', 'N/A')[:20]}")

        # 查看x和y坐标的分布
        x_values = [c['x0'] for c in chars]
        y_values = [c['top'] for c in chars]

        print(f"\nX坐标范围: {min(x_values):.1f} - {max(x_values):.1f}")
        print(f"Y坐标范围: {min(y_values):.1f} - {max(y_values):.1f}")

        # 统计不同的x坐标（列）
        unique_x = sorted(set([round(c['x0'], 1) for c in chars]))
        print(f"\n不同的X坐标数量（列数）: {len(unique_x)}")
        print(f"前10个X坐标: {unique_x[:10]}")

        # 统计不同的y坐标（行）
        unique_y = sorted(set([round(c['top'], 1) for c in chars]))
        print(f"\n不同的Y坐标数量（行数）: {len(unique_y)}")
        print(f"前10个Y坐标: {unique_y[:10]}")

if __name__ == "__main__":
    src = r"D:\EBook\fo\楞严经OCR\大佛顶首楞严经讲义[圆瑛法师].pdf"
    debug_pdf(src, page_num=3)  # 查看第3页
