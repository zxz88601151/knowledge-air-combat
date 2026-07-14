#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""合并509题到questions.json"""
import json, os

SCRIPT_DIR = os.path.dirname(__file__)
GEN_PATH = os.path.join(SCRIPT_DIR, "generated_g3_full.json")
EXISTING_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "questions.json")
LEVELS_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "levels.json")

with open(GEN_PATH, "r", encoding="utf-8") as f:
    new_qs = json.load(f)

with open(EXISTING_PATH, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_ids = set(q['id'] for q in existing)
new_qs = [q for q in new_qs if q['id'] not in existing_ids]

merged = existing + new_qs
merged.sort(key=lambda q: q['id'])

with open(EXISTING_PATH, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

g3_count = len([q for q in merged if q['subject'] == 'chinese_g3'])
print(f"合并完成!")
print(f"  原有: {len(existing)} 题")
print(f"  新增: {len(new_qs)} 题")
print(f"  合计: {len(merged)} 题")
print(f"  chinese_g3: {g3_count} 题")

from collections import Counter
kp = Counter(q['knowledge'] for q in merged if q['subject'] == 'chinese_g3')
print(f"\n三年级上学期知识点分布 (前30):")
for k, c in kp.most_common(30):
    print(f"  {k}: {c}题")

# 更新关卡题数
with open(LEVELS_PATH, "r", encoding="utf-8") as f:
    levels = json.load(f)

g3_levels = [l for l in levels if l['subject'] == 'chinese_g3']
print(f"\n三年级关卡: {len(g3_levels)} 关")
for l in g3_levels:
    # 计算该关卡的题数
    count = len([q for q in merged if q['subject'] == 'chinese_g3' 
                 and any(kf in q.get('knowledge','') for kf in l['knowledgeFilter'])])
    print(f"  Level {l['id']}: {l['name']} - 题库约{count}题 (关卡设{l['questionCount']}题)")
