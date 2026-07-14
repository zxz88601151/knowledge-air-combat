#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""深度提取PDF中每一课的完整文本，按课文组织"""
import fitz, re, json, os

PDF_PATH = "E:/知识空战项目/三年级上册.pdf"
doc = fitz.open(PDF_PATH)

# 提取所有文本
full_text = ""
for i, page in enumerate(doc):
    text = page.get_text()
    full_text += f"\n---PAGE {i+1}---\n{text}"

doc.close()

# 保存原始文本
out_dir = os.path.join("E:/知识空战项目/scripts")
os.makedirs(out_dir, exist_ok=True)
with open(os.path.join(out_dir, "pdf_full_text.txt"), "w", encoding="utf-8") as f:
    f.write(full_text)

# 提取每课的文本范围
lesson_patterns = [
    (r'第1课\s+大青树下的小学', '大青树下的小学', 1),
    (r'第2课\s+花的学校', '花的学校', 1),
    (r'第3课\s+不懂就要问', '不懂就要问', 1),
    (r'第4课\s+古诗三首', '古诗三首-第二单元', 2),
    (r'第5课\s+铺满金色巴掌的水泥道', '铺满金色巴掌的水泥道', 2),
    (r'第6课\s+秋天的雨', '秋天的雨', 2),
    (r'第7课\s+听听，秋的声音', '听听秋的声音', 2),
    (r'第8课\s+总也倒不了的老屋', '总也倒不了的老屋', 3),
    (r'第9课\s+犟龟', '犟龟', 3),
    (r'第10课\s+小狗学叫', '小狗学叫', 3),
    (r'第11课\s+宝葫芦的秘密', '宝葫芦的秘密', 4),
    (r'第12课\s+在牛肚子里旅行', '在牛肚子里旅行', 4),
    (r'第13课\s+一块奶酪', '一块奶酪', 4),
    (r'第14课\s+搭船的鸟', '搭船的鸟', 5),
    (r'第15课\s+金色的草地', '金色的草地', 5),
    (r'第16课\s+富饶的西沙群岛', '富饶的西沙群岛', 6),
    (r'第17课\s+海滨小城', '海滨小城', 6),
    (r'第18课\s+美丽的小兴安岭', '美丽的小兴安岭', 6),
    (r'第19课\s+香港，璀璨的明珠', '香港璀璨的明珠', 6),
    (r'第20课\s+古诗三首', '古诗三首-第七单元', 7),
    (r'第21课\s+大自然的声音', '大自然的声音', 7),
    (r'第22课\s+读不完的大书', '读不完的大书', 7),
    (r'第23课\s+司马光', '司马光', 8),
    (r'第24课\s+一定要争气', '一定要争气', 8),
    (r'第25课\s+手术台就是阵地', '手术台就是阵地', 8),
    (r'第26课\s+一个粗瓷大碗', '一个粗瓷大碗', 8),
]

print("PDF加载完成，共提取文本")
print(f"总字符数: {len(full_text)}")

# 提取各单元课文列表和结构
print("\n教材结构:")
units = re.findall(r'第[一二三四五六七八九十]+单元[^\n]*', full_text)
for u in units:
    print(f"  {u.strip()}")

print("\n课文列表:")
for pattern, name, unit_num in lesson_patterns:
    if re.search(pattern, full_text[:50000]):
        marker = " ✅" 
    else:
        marker = ""
    print(f"  第{unit_num}单元: {name}{marker}")

# 提取词语表和生字表
shengzi_section = full_text[full_text.find("识字表"):full_text.find("识字表")+5000] if "识字表" in full_text else ""
xiezi_section = full_text[full_text.find("写字表"):full_text.find("写字表")+5000] if "写字表" in full_text else ""
ciyu_section = full_text[full_text.find("词语表"):] if "词语表" in full_text else ""

print(f"\n识字表内容长度: {len(shengzi_section)} 字符")
print(f"写字表内容长度: {len(xiezi_section)} 字符")
print(f"词语表内容长度: {len(ciyu_section)} 字符")

# 提取课后生字
print("\n=== 识字表(前300字) ===")
print(shengzi_section[:300])

print("\n=== 词语表(前300字) ===")
print(ciyu_section[:300])

output = {
    "total_chars": len(full_text),
    "lessons": [{"unit": u, "name": n} for u, n in zip([1]*7+[2]*4+[3]*3+[4]*3+[5]*2+[6]*4+[7]*3+[8]*4,
                                                       ['大青树下的小学','花的学校','不懂就要问','古诗三首(望洞庭/山行/夜书所见)','铺满金色巴掌的水泥道','秋天的雨','听听秋的声音',
                                                        '总也倒不了的老屋','犟龟','小狗学叫',
                                                        '宝葫芦的秘密','在牛肚子里旅行','一块奶酪',
                                                        '搭船的鸟','金色的草地',
                                                        '富饶的西沙群岛','海滨小城','美丽的小兴安岭','香港璀璨的明珠',
                                                        '古诗三首(鹿柴/望天门山/饮湖上初晴后雨)','大自然的声音','读不完的大书',
                                                        '司马光','一定要争气','手术台就是阵地','一个粗瓷大碗'])],
    "shengzi_section": shengzi_section[:2000],
    "ciyu_section": ciyu_section[:2000],
}

with open(os.path.join(out_dir, "textbook_structure.json"), "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\n结构数据已保存")
