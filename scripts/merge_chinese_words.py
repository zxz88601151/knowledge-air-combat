#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""合并语文非古诗题到 questions.json + 更新 levels.json"""
import json
import os

SCRIPT_DIR = os.path.dirname(__file__)
GEN_PATH = os.path.join(SCRIPT_DIR, "generated_chinese_words.json")
EXISTING_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "questions.json")
LEVELS_PATH = os.path.join(SCRIPT_DIR, "..", "src", "data", "levels.json")
MODESELECT_PATH = os.path.join(SCRIPT_DIR, "..", "src", "game", "ModeSelectScene.ts")

# ================================================================
#  1. 读取并合并题目
# ================================================================
with open(GEN_PATH, "r", encoding="utf-8") as f:
    new_questions = json.load(f)

with open(EXISTING_PATH, "r", encoding="utf-8") as f:
    existing = json.load(f)

existing_ids = set(q['id'] for q in existing)
new_questions = [q for q in new_questions if q['id'] not in existing_ids]

merged = existing + new_questions
merged.sort(key=lambda q: q['id'])

with open(EXISTING_PATH, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)

print(f"题库合并完成！")
print(f"  原有: {len(existing)} 题")
print(f"  新增: {len(new_questions)} 题")
print(f"  合并: {len(merged)} 题")

math_c = len([q for q in merged if q['subject'] == 'math_su'])
chn_c = len([q for q in merged if q['subject'] == 'chinese'])
print(f"  数学: {math_c} 题, 语文: {chn_c} 题")

# ================================================================
#  2. 更新 levels.json - 新增 2 个语文非古诗关卡
# ================================================================
with open(LEVELS_PATH, "r", encoding="utf-8") as f:
    levels = json.load(f)

# 检查是否已存在
existing_level_ids = set(l['id'] for l in levels)
if 10 not in existing_level_ids:
    levels.append({
        "id": 10,
        "name": "拼音识字区",
        "description": "看拼音写词语、量词搭配、近义词反义词——语文基础训练",
        "subject": "chinese",
        "questionCount": 14,
        "enemySpeed": 28,
        "enemyCount": 3,
        "distractorCount": 2,
        "movePatterns": ["down"],
        "knowledgeFilter": ["看拼音写词语", "量词搭配", "近反义词"],
        "difficultyRange": [1, 1],
        "typeFilter": ["fill"]
    })
    print(f"新增 Level 10: 拼音识字区")
else:
    print(f"Level 10 已存在，跳过")

if 11 not in existing_level_ids:
    levels.append({
        "id": 11,
        "name": "字词大挑战",
        "description": "多音字辨析、形近字辨析、词语理解——进阶字词能力",
        "subject": "chinese",
        "questionCount": 12,
        "enemySpeed": 32,
        "enemyCount": 3,
        "distractorCount": 2,
        "movePatterns": ["down"],
        "knowledgeFilter": ["多音字", "形近字", "词语理解"],
        "difficultyRange": [1, 2],
        "typeFilter": ["fill"]
    })
    print(f"新增 Level 11: 字词大挑战")
else:
    print(f"Level 11 已存在，跳过")

with open(LEVELS_PATH, "w", encoding="utf-8") as f:
    json.dump(levels, f, ensure_ascii=False, indent=2)

print(f"Levels 已更新: 共 {len(levels)} 关")

# ================================================================
#  3. 更新 ModeSelectScene.ts - 显示题数
# ================================================================
with open(MODESELECT_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 替换显示数字
import re
content = re.sub(
    r'(\d+) 道核心题',
    f'{math_c} 道核心题',
    content
)
content = re.sub(
    r'(\d+) 首古诗题',
    f'{chn_c} 首古诗题',
    content
)

# 如果语文题数超过古诗，更新描述
content = content.replace(
    '44 首古诗题',
    f'{chn_c} 道语文题'
)

with open(MODESELECT_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print(f"ModeSelectScene.ts 已更新")
print(f"  数学: {math_c} 题")
print(f"  语文: {chn_c} 题")
