#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""PDF内容提取 + 知识点分析"""
import fitz
import json
import os
from collections import Counter

PDF_PATH = "E:/知识空战项目/三年级上册.pdf"
OUTPUT_DIR = "E:/知识空战项目/scripts"

doc = fitz.open(PDF_PATH)
print(f"PDF 总页数: {doc.page_count}")

# 提取全文
full_text = ""
for i, page in enumerate(doc):
    text = page.get_text()
    full_text += f"\n--- 第{i+1}页 ---\n{text}"

print(f"总字符数: {len(full_text)}")

# 保存全文到文本文件
txt_path = os.path.join(os.path.dirname(__file__) if "__file__" in dir() else "E:/知识空战项目/scripts", "三年级上册_全文.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    f.write(full_text)

# 分析目录/章节结构
print("\n" + "="*60)
print("章节结构分析")
print("="*60)

# 查找章节标题
import re
lines = full_text.split('\n')
chapters = []
for line in lines:
    line = line.strip()
    # 匹配常见章节标题格式
    if re.match(r'^第[一二三四五六七八九十]+单元', line):
        chapters.append(("UNIT", line))
    elif re.match(r'^\d+\s*\.?\s*[^\d]', line) and len(line) > 3 and len(line) < 60:
        if any(kw in line for kw in ['课文', '识', '园地', '语文', '口语', '习作', '古诗', '阅读']):
            chapters.append(("LESSON", line))

print("\n检测到的结构:")
for typ, title in chapters:
    print(f"  [{typ}] {title}")

# 分析知识点关键词
print("\n" + "="*60)
print("知识点关键词频率分析")
print("="*60)

keywords_sentences = []
keyword_patterns = [
    '多音字', '形近字', '近义词', '反义词', '量词', '词语', '拼音',
    '音调', '声调', '偏旁', '部首', '笔画', '笔顺', '结构', '组词',
    '造句', '成语', '古诗', '课文', '理解', '背诵', '默写',
    '音节', '韵母', '声母', '整体认读音节',
    '描写', '比喻', '拟人', '排比', '夸张', '修辞',
    '标点', '句号', '逗号', '问号', '感叹号',
    '日积月累', '识字', '写字',
]

# 查找包含知识点的句子
for line in lines:
    line = line.strip()
    if len(line) < 5 or len(line) > 200:
        continue
    found = [kw for kw in keyword_patterns if kw in line]
    if found:
        keywords_sentences.append((found, line))

print(f"\n包含知识点的句子数: {len(keywords_sentences)}")
print("\n按知识点分类:")
kp_counter = Counter()
for found, _ in keywords_sentences:
    for kw in found:
        kp_counter[kw] += 1

for kw, count in kp_counter.most_common(30):
    print(f"  {kw}: {count}次")

# 输出各单元全文摘要
print("\n" + "="*60)
print("各单元内容摘要")
print("="*60)

current_unit = ""
unit_texts = {}
for line in lines:
    line = line.strip()
    if not line:
        continue
    m = re.match(r'^第[一二三四五六七八九十]+单元', line)
    if m:
        current_unit = line
        unit_texts[current_unit] = []
    elif current_unit and line not in unit_texts.get(current_unit, []):
        if current_unit not in unit_texts:
            unit_texts[current_unit] = []
        unit_texts[current_unit].append(line[:100])

for unit, texts in unit_texts.items():
    print(f"\n--- {unit} ---")
    # 提取关键词
    unit_text = ' '.join(texts)
    unit_keywords = []
    for kw in keyword_patterns:
        if kw in unit_text:
            unit_keywords.append(kw)
    if unit_keywords:
        print(f"  知识点: {', '.join(unit_keywords[:10])}")
    # 显示前5个非空行
    count = 0
    for t in texts[:8]:
        if t.strip():
            print(f"  {t[:80]}")
            count += 1
    if count >= 8:
        print(f"  ... 共 {len(texts)} 行")

doc.close()
print(f"\n全文已保存到: {txt_path}")
