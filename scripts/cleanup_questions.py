#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""质量修复：删除选项为ABC标签的题目 + 删除重复题"""
import json, os
from collections import Counter

PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "questions.json")

with open(PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"原始总数: {len(data)}")

removed_reasons = Counter()
keep = []

for q in data:
    qid = q['id']
    opts = [o.strip() for o in q.get('options', [])]
    qtext = q.get('question', '')
    
    # 规则1：所有选项都是单字母(A/B/C/D)或单数字标签
    all_abc_labels = all(o in ('A','B','C','D','E') for o in opts)
    if all_abc_labels:
        removed_reasons['选项为A/B/C标签'] += 1
        continue
    
    # 规则2：模糊选项（不知道/不确定/都不对）且无实际内容
    fuzzy_only = all(o in ('不知道','不确定','都不对','其他') for o in opts)
    if fuzzy_only:
        removed_reasons['全模糊选项'] += 1
        continue
    
    # 规则3：答案不在选项中（数据损坏）
    if q.get('answer','') not in opts:
        removed_reasons['答案不在选项中'] += 1
        continue
    
    keep.append(q)

# 规则4：去除完全重复的题目（保留ID小的）
seen_questions = {}
final = []
for q in keep:
    key = q.get('question','').strip().rstrip('？?').rstrip('?')
    if key in seen_questions:
        removed_reasons['重复题目'] += 1
        continue
    seen_questions[key] = q['id']
    final.append(q)

final.sort(key=lambda q: q['id'])

print(f"\n删除统计:")
for reason, count in removed_reasons.most_common():
    print(f"  {reason}: {count}题")
print(f"\n保留: {len(final)} 题")
print(f"删除: {len(data) - len(final)} 题")

# 按科目统计
subj = Counter(q['subject'] for q in final)
for s, c in subj.most_common():
    print(f"  {s}: {c}题")

with open(PATH, "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

print(f"\n已保存清理后数据到 {PATH}")
