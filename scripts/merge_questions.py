#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""
合并生成的题目到 questions.json
1. 规范知识点命名（chinese 用 "古诗-山行" 格式）
2. 补充缺失的《望洞庭》4题
3. 修正小问题（如 id 147 的 1.5 小数选项）
4. 合并到 src/data/questions.json
"""
import json
import os

SCRIPT_DIR = os.path.dirname(__file__)
GEN_PATH = os.path.join(SCRIPT_DIR, "generated_questions.json")
EXISTING_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "questions.json")

# ================================================================
#  1. 读取生成的题目
# ================================================================
with open(GEN_PATH, "r", encoding="utf-8") as f:
    generated = json.load(f)

# ================================================================
#  2. 规范知识点命名
# ================================================================
# 将 chinese 的知识点从 "古诗《山行》" 改为 "古诗-山行"（与现有一致）
for q in generated:
    if q['subject'] == 'chinese':
        for old_prefix, new_prefix in [
            ('古诗《', '古诗-'),
            ('》', ''),
        ]:
            q['knowledge'] = q['knowledge'].replace('古诗《', '古诗-').replace('》', '')

# ================================================================
#  3. 补充《望洞庭》4题（id 181-184）
# ================================================================
new_id = max(q['id'] for q in generated) + 1

望洞庭_questions = [
    {
        "id": new_id,
        "subject": "chinese",
        "type": "fill",
        "question": '\u300a\u671b\u6d1e\u5ead\u300b\u4e2d\u201c\u6e56\u5149\u79cb\u6708\u4e24\u76f8\u548c\u201d\u7684\u4e0b\u4e00\u53e5\u662f\uff1f',
        "answer": '\u6f6d\u9762\u65e0\u98ce\u955c\u672a\u78e8',
        "options": ['\u6f6d\u9762\u65e0\u98ce\u955c\u672a\u78e8', '\u767d\u94f6\u76d8\u91cc\u4e00\u9752\u87ba', '\u6708\u843d\u4e4c\u557c\u971c\u6ee1\u5929'],
        "explain": '\u5168\u8bd7\uff1a\u6e56\u5149\u79cb\u6708\u4e24\u76f8\u548c\uff0c\u6f6d\u9762\u65e0\u98ce\u955c\u672a\u78e8\u3002\u9065\u671b\u6d1e\u5ead\u5c71\u6c34\u7fe0\uff0c\u767d\u94f6\u76d8\u91cc\u4e00\u9752\u87ba\u3002',
        "difficulty": 1,
        "knowledge": "\u53e4\u8bd7-\u671b\u6d1e\u5ead"
    },
    {
        "id": new_id + 1,
        "subject": "chinese",
        "type": "fill",
        "question": '\u300a\u671b\u6d1e\u5ead\u300b\u4e2d\u201c\u9065\u671b\u6d1e\u5ead\u5c71\u6c34\u7fe0\u201d\u7684\u4e0b\u4e00\u53e5\u662f\uff1f',
        "answer": '\u767d\u94f6\u76d8\u91cc\u4e00\u9752\u87ba',
        "options": ['\u767d\u94f6\u76d8\u91cc\u4e00\u9752\u87ba', '\u6f6d\u9762\u65e0\u98ce\u955c\u672a\u78e8', '\u767d\u7389\u76d8\u4e2d\u4e00\u9752\u87ba'],
        "explain": '\u5168\u8bd7\uff1a\u9065\u671b\u6d1e\u5ead\u5c71\u6c34\u7fe0\uff0c\u767d\u94f6\u76d8\u91cc\u4e00\u9752\u87ba\u3002\u8fdc\u671b\u6d1e\u5ead\u5c71\u6c34\u5982\u767d\u94f6\u76d8\u91cc\u6258\u7740\u4e00\u679a\u9752\u87ba\u3002',
        "difficulty": 1,
        "knowledge": "\u53e4\u8bd7-\u671b\u6d1e\u5ead"
    },
    {
        "id": new_id + 2,
        "subject": "chinese",
        "type": "fill",
        "question": '\u300a\u671b\u6d1e\u5ead\u300b\u7684\u4f5c\u8005\u662f\u8c01\uff1f',
        "answer": '\u5218\u79b9\u9521',
        "options": ['\u5218\u79b9\u9521', '\u675c\u752b', '\u767d\u5c45\u6613'],
        "explain": '\u300a\u671b\u6d1e\u5ead\u300b\u662f\u5510\u4ee3\u8bd7\u4eba\u5218\u79b9\u9521\u7684\u4f5c\u54c1\u3002',
        "difficulty": 1,
        "knowledge": "\u53e4\u8bd7-\u671b\u6d1e\u5ead"
    },
    {
        "id": new_id + 3,
        "subject": "chinese",
        "type": "fill",
        "question": '\u300a\u671b\u6d1e\u5ead\u300b\u4e2d\u201c\u955c\u672a\u78e8\u201d\u5f62\u5bb9\u7684\u662f\u4ec0\u4e48\uff1f',
        "answer": '\u6e56\u9762\u5e73\u9759',
        "options": ['\u6e56\u9762\u5e73\u9759', '\u955c\u5b50\u6ca1\u78e8', '\u6708\u4eae\u672a\u5706'],
        "explain": '\u201c\u955c\u672a\u78e8\u201d\u7528\u672a\u6253\u78e8\u7684\u94dc\u955c\u6bd4\u55bb\u98ce\u5e73\u6d6a\u9759\u7684\u6e56\u9762\uff0c\u8fd0\u7528\u4e86\u6bd4\u55bb\u7684\u4fee\u8f9e\u624b\u6cd5\u3002',
        "difficulty": 2,
        "knowledge": "\u53e4\u8bd7-\u671b\u6d1e\u5ead"
    },
]

# ================================================================
#  4. 修正 id 147（千克和克）的选项：去掉小数 1.5
# ================================================================
for q in generated:
    if q['id'] == 147:
        q['options'] = ['2', '3', '2000']
        if q['answer'] == '2':
            q['options'][0] = '2'
        break

# ================================================================
#  5. 合并
# ================================================================
all_new = generated + 望洞庭_questions

# 读取现有题库
with open(EXISTING_PATH, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_ids = set(q['id'] for q in existing)
new_ids = set(q['id'] for q in all_new)
overlap = existing_ids & new_ids

if overlap:
    print(f"警告：ID 冲突 {overlap}，跳过冲突项")
    all_new = [q for q in all_new if q['id'] not in overlap]

# 合并
merged = existing + all_new
merged.sort(key=lambda q: q['id'])

# ================================================================
#  6. 输出
# ================================================================
with open(EXISTING_PATH, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"合并完成！")
print(f"  原有题库: {len(existing)} 题")
print(f"  新增题目: {len(all_new)} 题")
print(f"  合并后: {len(merged)} 题")
print(f"  文件: {EXISTING_PATH}")

# 统计
math_new = len([q for q in all_new if q['subject'] == 'math_su'])
chn_new = len([q for q in all_new if q['subject'] == 'chinese'])
print(f"\n新增分布:")
print(f"  数学: {math_new} 题")
print(f"  语文: {chn_new} 题")

from collections import Counter
kp = Counter(q['knowledge'] for q in all_new)
print(f"\n新增知识点:")
for k, c in kp.most_common():
    print(f"  {k}: {c}题")

print(f"\n建议同步更新 ModeSelectScene.ts:")
print(f"  数学题数: {len([q for q in merged if q['subject']=='math_su'])}")
print(f"  语文题数: {len([q for q in merged if q['subject']=='chinese'])}")
