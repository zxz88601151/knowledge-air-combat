#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""修复关卡知识过滤器以匹配实际生成的题目"""
import json, os

LEVELS_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "levels.json")
QUESTIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "questions.json")

with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
    questions = json.load(f)

with open(LEVELS_PATH, "r", encoding="utf-8") as f:
    levels = json.load(f)

g3_questions = [q for q in questions if q['subject'] == 'chinese_g3']
print(f"chinese_g3 总题数: {len(g3_questions)}")

# 查看所有独特的知识点标签
from collections import Counter
all_kp = Counter(q['knowledge'] for q in g3_questions)
print(f"\n独特点标签总数: {len(all_kp)}")
print(f"高频标签 (>5题):")
for k, c in all_kp.most_common(40):
    if c >= 5:
        print(f"  {k}: {c}题")

# 按关键词分组标签
tag_groups = {
    "大青树下的小学": [k for k in all_kp if '大青树' in k or '大青树下' in k],
    "花的学校": [k for k in all_kp if '花的学校' in k],
    "不懂就要问": [k for k in all_kp if '不懂就要问' in k],
    "语文园地一": [k for k in all_kp if '语文园地一' in k or ('园地' in k and '日积月累' in k)],
    "望洞庭": [k for k in all_kp if '望洞庭' in k or '山行' in k or '夜书所见' in k or ('古诗' in k and '日积月累' in k)],
    "铺满金色巴掌的水泥道": [k for k in all_kp if '铺满' in k or '水泥道' in k or '巴掌' in k],
    "秋天的雨": [k for k in all_kp if '秋天的雨' in k],
    "听听秋的声音": [k for k in all_kp if '听听' in k or '秋的声音' in k],
    "语文园地二": [k for k in all_kp if '语文园地二' in k or ('园地' in k and '日记' in k)],
    "总也倒不了的老屋": [k for k in all_kp if '老屋' in k],
    "犟龟": [k for k in all_kp if '犟龟' in k],
    "小狗学叫": [k for k in all_kp if '小狗学叫' in k or '小狗' in k],
    "语文园地三": [k for k in all_kp if '语文园地三' in k],
    "宝葫芦的秘密": [k for k in all_kp if '宝葫芦' in k],
    "在牛肚子里旅行": [k for k in all_kp if '牛肚子' in k or '红头' in k],
    "一块奶酪": [k for k in all_kp if '奶酪' in k],
    "语文园地四": [k for k in all_kp if '语文园地四' in k],
    "搭船的鸟": [k for k in all_kp if '搭船' in k or '翠鸟' in k],
    "金色的草地": [k for k in all_kp if '金色的草地' in k or '蒲公英' in k],
    "语文园地五": [k for k in all_kp if '语文园地五' in k],
    "富饶的西沙群岛": [k for k in all_kp if '西沙群岛' in k],
    "海滨小城": [k for k in all_kp if '海滨小城' in k],
    "美丽的小兴安岭": [k for k in all_kp if '小兴安岭' in k],
    "语文园地六": [k for k in all_kp if '语文园地六' in k],
    "鹿柴": [k for k in all_kp if '鹿柴' in k or '望天门山' in k or '饮湖上初晴' in k],
    "大自然的声音": [k for k in all_kp if '大自然的声音' in k],
    "读不完的大书": [k for k in all_kp if '读不完的大书' in k],
    "语文园地七": [k for k in all_kp if '语文园地七' in k],
    "司马光": [k for k in all_kp if '司马光' in k],
    "一定要争气": [k for k in all_kp if '一定要争气' in k or '童第周' in k],
    "手术台就是阵地": [k for k in all_kp if '手术台' in k or '白求恩' in k],
    "一个粗瓷大碗": [k for k in all_kp if '粗瓷大碗' in k or '赵一曼' in k],
    "语文园地八": [k for k in all_kp if '语文园地八' in k],
}

# 更新levels
for level in levels:
    if level['subject'] != 'chinese_g3':
        continue
    
    # 根据关卡名匹配标签组
    name = level['name']
    tags = ['三年级-其他', '三年级-多音字', '三年级-词语积累', '三年级-词语理解']  # 通用标签
    
    for group_name, group_tags in tag_groups.items():
        if group_name in name or any(kw in name for kw in group_name.split()):
            tags.extend(group_tags)
            break
    
    # 去重
    tags = list(dict.fromkeys(tags))
    level['knowledgeFilter'] = tags
    
    # 统计该关卡可用的题数
    available = len([q for q in g3_questions if any(f in q.get('knowledge','') for f in tags)])
    print(f"  Level {level['id']} {level['name']}: filter={len(tags)}个标签, 可用约{available}题")

with open(LEVELS_PATH, "w", encoding="utf-8") as f:
    json.dump(levels, f, ensure_ascii=False, indent=2)

print(f"\n关卡知识过滤器已更新!")
