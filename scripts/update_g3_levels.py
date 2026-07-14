#!/usr/bin/env python3
# © 中哥  All Rights Reserved
# 版权标识: FP_UUID_31adb5871aea40b8b0c288773f094ab2|FP_AUTHOR_中哥_SN_20260531|FP_HASH_20260531B9F3|FP_ORIGIN_2026_AUTHOR_中哥
# 仅限项目内部使用，未经授权禁止转载、商用。

"""更新 levels.json - 为每篇课文创建独立关卡（Level 14-45）"""
import json, os

LEVELS_PATH = os.path.join(os.path.dirname(__file__), "..", "src", "data", "levels.json")
GEN_PATH = os.path.join(os.path.dirname(__file__), "generated_g3_full.json")

# 读取现有levels
with open(LEVELS_PATH, "r", encoding="utf-8") as f:
    levels = json.load(f)

# 去掉旧的 chinese_g3 levels (id 12-13)
levels = [l for l in levels if l['subject'] != 'chinese_g3']

# 定义每课的关卡配置
LESSON_LEVELS = [
    # (id, name, description, knowledge_prefix, count)
    # 第一单元
    (14, "大青树下的小学", "第一单元课文", "大青树下的小学", 8),
    (15, "花的学校", "第一单元课文", "花的学校", 8),
    (16, "不懂就要问", "第一单元课文", "不懂就要问", 8),
    (17, "语文园地一", "第一单元语文园地", "语文园地一", 6),
    # 第二单元
    (18, "古诗三首(望洞庭/山行/夜书所见)", "第二单元古诗", "望洞庭|山行|夜书所见", 10),
    (19, "铺满金色巴掌的水泥道", "第二单元课文", "铺满金色巴掌的水泥道", 8),
    (20, "秋天的雨", "第二单元课文", "秋天的雨", 8),
    (21, "听听秋的声音", "第二单元课文", "听听秋的声音", 8),
    (22, "语文园地二", "第二单元语文园地", "语文园地二", 6),
    # 第三单元
    (23, "总也倒不了的老屋", "第三单元课文", "总也倒不了的老屋", 8),
    (24, "犟龟", "第三单元课文", "犟龟", 8),
    (25, "小狗学叫", "第三单元课文", "小狗学叫", 8),
    (26, "语文园地三", "第三单元语文园地", "语文园地三", 6),
    # 第四单元
    (27, "宝葫芦的秘密", "第四单元课文", "宝葫芦的秘密", 8),
    (28, "在牛肚子里旅行", "第四单元课文", "在牛肚子里旅行", 8),
    (29, "一块奶酪", "第四单元课文", "一块奶酪", 8),
    (30, "语文园地四", "第四单元语文园地", "语文园地四", 6),
    # 第五单元
    (31, "搭船的鸟", "第五单元课文", "搭船的鸟", 8),
    (32, "金色的草地", "第五单元课文", "金色的草地", 8),
    (33, "语文园地五", "第五单元语文园地", "语文园地五", 6),
    # 第六单元
    (34, "富饶的西沙群岛", "第六单元课文", "富饶的西沙群岛", 8),
    (35, "海滨小城", "第六单元课文", "海滨小城", 8),
    (36, "美丽的小兴安岭", "第六单元课文", "美丽的小兴安岭", 8),
    (37, "语文园地六", "第六单元语文园地", "语文园地六", 6),
    # 第七单元
    (38, "古诗三首(鹿柴/望天门山/饮湖上初晴后雨)", "第七单元古诗", "鹿柴|望天门山|饮湖上初晴后雨", 10),
    (39, "大自然的声音", "第七单元课文", "大自然的声音", 8),
    (40, "读不完的大书", "第七单元课文", "读不完的大书", 8),
    (41, "语文园地七", "第七单元语文园地", "语文园地七", 6),
    # 第八单元
    (42, "司马光", "第八单元课文", "司马光", 8),
    (43, "一定要争气", "第八单元课文", "一定要争气", 8),
    (44, "手术台就是阵地", "第八单元课文", "手术台就是阵地", 8),
    (45, "语文园地八", "第八单元语文园地", "语文园地八", 6),
]

for lid, name, desc, kp, count in LESSON_LEVELS:
    # 构建knowledgeFilter（支持|分隔的多个标签）
    kf = [f"三年级-{tag.strip()}" for tag in kp.split('|')]
    levels.append({
        "id": lid,
        "name": name[:20],
        "description": desc,
        "subject": "chinese_g3",
        "questionCount": count,
        "enemySpeed": 28,
        "enemyCount": 3,
        "distractorCount": 2,
        "movePatterns": ["down"],
        "knowledgeFilter": kf,
        "difficultyRange": [1, 2],
        "typeFilter": ["fill"],
    })

levels.sort(key=lambda x: x['id'])

with open(LEVELS_PATH, "w", encoding="utf-8") as f:
    json.dump(levels, f, ensure_ascii=False, indent=2)

print(f"Levels更新完成！共 {len(levels)} 关")
print(f"chinese_g3 关卡: 14-45（共32关）")

# 统计
g3_levels = [l for l in levels if l['subject'] == 'chinese_g3']
print(f"\n三年级上学期关卡列表:")
for l in g3_levels:
    print(f"  Level {l['id']}: {l['name']} ({l['questionCount']}题)")
