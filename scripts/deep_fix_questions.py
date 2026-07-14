#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""深度修复：清理选项前缀 + 统一知识标签 + 补充难度"""
import json, os, re

PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "questions.json")

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

fixes = {
    'prefix_cleaned': 0,
    'knowledge_unified': 0,
    'difficulty_adjusted': 0,
}

for q in data:
    if q['subject'] != 'chinese_g3':
        continue
    
    # ===== 修复1: 选项前缀清理 =====
    # 去掉"A. ", "B. ", "C. ", "D. " 前缀
    # 以及选项为单个"A"/"B"/"C"的问题
    opts = q.get('options', [])
    cleaned = []
    for o in opts:
        o = o.strip()
        # 去掉 "A. xxx" → "xxx"
        o = re.sub(r'^[A-Da-d][.、．]\s*', '', o)
        # 如果清理后是空或者只是A/B/C，尝试用下一个选项补充
        cleaned.append(o)
    
    # 如果某个选项只剩单字母且其他选项有内容，尝试修复
    valid_opts = [o for o in cleaned if len(o) > 2 or (len(o) <= 2 and o.isdigit())]
    if len(valid_opts) >= 3:
        q['options'] = valid_opts[:3]
        fixes['prefix_cleaned'] += 1
    else:
        q['options'] = cleaned  # 保持原样
    
    # ===== 修复2: "三年级-其他"改为更具体的标签 =====
    if q.get('knowledge') == '三年级-其他':
        qtext = q.get('question', '')
        # 尝试从题目文本推断知识点
        if '多音字' in qtext or '读音' in qtext or '读什么' in qtext:
            q['knowledge'] = '三年级-多音字'
        elif '成语' in qtext or '摇头晃脑' in qtext or '面红耳赤' in qtext:
            q['knowledge'] = '三年级-成语积累'
        elif '近义词' in qtext or '反义词' in qtext:
            q['knowledge'] = '三年级-词语积累'
        elif '部首' in qtext or '笔画' in qtext or '结构' in qtext:
            q['knowledge'] = '三年级-生字'
        elif '古诗' in qtext or '诗' in qtext and '课文' not in qtext:
            q['knowledge'] = '三年级-古诗'
        elif '课文' in qtext or '作者' in qtext:
            q['knowledge'] = '三年级-课文理解'
        else:
            # 保留为其他
            pass
        fixes['knowledge_unified'] += 1
    
    # ===== 修复3: 难度补充 =====
    if q.get('difficulty', 1) == 1:
        qtext = q.get('question', '')
        # 某些题型应该更难
        if '多音字' in q['knowledge'] and ('选择正确读音' in qtext or '与其他不同' in qtext):
            q['difficulty'] = 2
            fixes['difficulty_adjusted'] += 1
        elif '成语' in q['knowledge'] and '使用正确' in qtext:
            q['difficulty'] = 2
            fixes['difficulty_adjusted'] += 1
        elif '笔画' in qtext or '笔顺' in qtext:
            q['difficulty'] = 2
            fixes['difficulty_adjusted'] += 1

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"修复统计:")
for fix_name, count in fixes.items():
    print(f"  {fix_name}: {count}处")

# 验证
print(f"\n验证清理效果:")
print(f"  含A.B.C前缀的选项:")
abc_count = 0
for q in data:
    for o in q.get('options', []):
        if re.match(r'^[A-Da-d][.、．]', o.strip()):
            abc_count += 1
            break
print(f"    剩余: {abc_count}处")

from collections import Counter
diff = Counter(q['difficulty'] for q in data if q['subject'] == 'chinese_g3')
print(f"  chinese_g3难度分布: {dict(sorted(diff.items()))}")

kp = Counter(q['knowledge'] for q in data if q['subject'] == 'chinese_g3')
print(f"  三年级-其他: {kp.get('三年级-其他', 0)}题")
