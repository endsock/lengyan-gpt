#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将楞严经讲记按卷分割成多个文件
"""

import os
import re

def split_by_volume(input_file, output_dir):
    """
    将输入文件按照卷标题分割成多个文件

    Args:
        input_file: 输入的markdown文件路径
        output_dir: 输出目录路径
    """
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"创建输出目录: {output_dir}")

    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 卷标题的正则表达式（注意是繁体"講義"）
    volume_pattern = r'## 大佛頂如來密因修證了義諸菩薩萬行首楞嚴經講義第(.+?)卷'

    # 查找所有卷标题的位置
    volumes = []
    for match in re.finditer(volume_pattern, content):
        volume_num = match.group(1)
        start_pos = match.start()
        volumes.append((volume_num, start_pos))

    print(f"找到 {len(volumes)} 卷")

    # 分割内容并写入文件
    for i, (volume_num, start_pos) in enumerate(volumes):
        # 确定结束位置
        if i < len(volumes) - 1:
            end_pos = volumes[i + 1][1]
        else:
            end_pos = len(content)

        # 提取当前卷的内容
        volume_content = content[start_pos:end_pos]

        # 构造输出文件名
        output_file = os.path.join(output_dir, f'楞严经义贯_第{volume_num}卷.md')

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(volume_content)

        print(f"已写入: {output_file}")

    print(f"\n分割完成！共生成 {len(volumes)} 个文件，保存在目录: {output_dir}")


if __name__ == '__main__':
    # 输入文件路径
    input_file = 'chengguan_all.md'

    # 输出目录
    output_dir = 'chengguan_doc'

    # 执行分割
    split_by_volume(input_file, output_dir)
