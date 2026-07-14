#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""深度提取PDF各单元的知识点细节"""
import fitz
import re
from collections import Counter

PDF_PATH = "E:/知识空战项目/三年级上册.pdf"
doc = fitz.open(PDF_PATH)

# 提取每个单元的内容
current_unit = ""
unit_pages = {}
unit_content = {}

for i, page in enumerate(doc):
    text = page.get_text()
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        m = re.match(r'^第([一二三四五六七八九十]+)单元', line)
        if m:
            current_unit = line
            unit_pages[current_unit] = []
            unit_content[current_unit] = ""
    if current_unit:
        unit_pages[current_unit].append(i + 1)
        unit_content[current_unit] += text + "\n"

print("=" * 60)
print("部编版 三年级上册 语文 知识点深度提取")
print("=" * 60)

# 各单元知识点提取
knowledge_points = {}

for unit_name in sorted(unit_content.keys(), key=lambda x: int(re.search(r'[一二三四五六七八九十]+', x).group().replace('一','1').replace('二','2').replace('三','3').replace('四','4').replace('五','5').replace('六','6').replace('七','7').replace('八','8').replace('九','9').replace('十','10') if re.search(r'[一二三四五六七八九十]+', x) else '0')):
    text = unit_content[unit_name]
    print(f"\n{'='*50}")
    pages = unit_pages.get(unit_name, [])
    print(f"  {unit_name} (第{pages[0] if pages else '?'}-{pages[-1] if pages else '?'}页)")
    print(f"{'='*50}")
    
    # 提取生字表
    shengzi = []
    for line in text.split('\n'):
        line = line.strip()
        # 匹配生字模式 - 带有拼音标注的字
        if re.match(r'^[a-zèéêëēėęěə]+$', line) and len(line) <= 10:
            continue
        if re.match(r'^[A-Z]', line) and len(line) <= 20:
            continue
        if len(line) >= 2 and len(line) <= 10 and re.search(r'[一-龥]', line):
            # 可能是生字
            chars = re.findall(r'[一-龥]', line)
            if chars:
                shengzi.extend(chars)
    
    # 提取"我会认"和"我会写"字表
    renzi = re.findall(r'(?:我会认|会认|认识|认一认)[：:：\s]*([^。\n]{3,60})', text)
    xiezi = re.findall(r'(?:我会写|会写|写一写)[：:：\s]*([^。\n]{3,60})', text)
    
    # 提取课后习题中的知识点
    exercises = re.findall(r'(?:想一想|说一说|读一读|抄一抄|背一背|填一填|练一练)[：:：\s]*([^。\n]{3,100})', text)
    
    # 提取多音字
    duoyin = re.findall(r'(?:多音字)[：:：\s]*([^。\n]{3,100})', text)
    
    # 提取语文园地中的知识点
    yuandi = re.findall(r'(?:语文园地|日积月累|识字加油站|词句段运用)[：:：\s]*([^。\n]{3,200})', text)
    
    # 提取近义词反义词
    jinyi = re.findall(r'(?:近义词|近义)[：:：\s]*([^。\n]{3,100})', text)
    fanyi = re.findall(r'(?:反义词|反义)[：:：\s]*([^。\n]{3,100})', text)
    
    # 提取成语/词语
    chengyu = re.findall(r'(?:成语|词语积累|四字词语)[：:：\s]*([^。\n]{3,100})', text)
    
    # 提取修辞
    xiuci = re.findall(r'(?:比喻|拟人|排比|夸张|修辞)[：:：\s]*([^。\n]{3,100})', text)
    
    print(f"\n  生字候选: {', '.join(list(set(shengzi))[:20])}")
    if renzi:
        print(f"  会认字: {'; '.join(renzi[:3])}")
    if xiezi:
        print(f"  会写字: {'; '.join(xiezi[:3])}")
    if duoyin:
        print(f"  多音字: {'; '.join(duoyin[:3])}")
    if jinyi:
        print(f"  近义词: {'; '.join(jinyi[:3])}")
    if fanyi:
        print(f"  反义词: {'; '.join(fanyi[:3])}")
    if chengyu:
        print(f"  成语/词语: {'; '.join(chengyu[:3])}")
    if xiuci:
        print(f"  修辞: {'; '.join(xiuci[:3])}")
    if exercises:
        print(f"  课后练习: {'; '.join(exercises[:3])}")
    if yuandi:
        print(f"  语文园地: {'; '.join(yuandi[:3])}")
    
    # 生字统计
    print(f"\n  课文篇章:")
    lessons = re.findall(r'^(\d+)\s+([^\d].{2,30})', text, re.MULTILINE)
    for num, title in lessons[:5]:
        print(f"    第{num}课 {title}")

print(f"\n{'='*60}")
print("PDF 内容提取完成!")
print(f"{'='*60}")

doc.close()
